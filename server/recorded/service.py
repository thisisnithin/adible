import os
from tempfile import NamedTemporaryFile
from uuid import uuid4
from domain.audio_file import get_audio_file_by_id, update_audio_status
from db import get_db_connection

from interface import determine_ad_placement, determine_optimal_voice_id, generate_ad_audio_with_nearby_audio, generate_advertisement_audio, generate_advertisements, insert_advertisement_audio, transcribe_audio_with_timestamps
from domain.transcription_segments import TranscriptionSegmentDb, get_transcription_segment_by_id, insert_transcription_segment
from domain.common import ProcessingStatus
from domain.generated_ad import GeneratedAd, get_generated_ad_by_id, insert_generated_ad
from domain.advertisement import get_advertisements
from domain.stitched_audio import update_stitched_audio_bytes, update_stitched_audio_status
from utils import sync_sheet_to_db

_ad_audio_cache = {}

def process_audio_file_and_generate_advertisements(audio_file_id: str):
    print(f"Starting processing for audio file {audio_file_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            sync_sheet_to_db(cursor)
            audio_file = get_audio_file_by_id(cursor, audio_file_id)
            if not audio_file:
                raise ValueError(f"Audio file with id {audio_file_id} not found")
            
            update_audio_status(cursor, audio_file_id, ProcessingStatus.PROCESSING)
            
            print(f"Creating temporary file for audio {audio_file_id}")
            temp_file = NamedTemporaryFile(delete=False)
            temp_file.write(audio_file.bytes)
            temp_file_path = temp_file.name
            temp_file.close()
            
            print(f"Starting transcription for {audio_file_id}")
            transcription_segments = transcribe_audio_with_timestamps(temp_file_path)
            print(f"Received {len(transcription_segments)} segments for {audio_file_id}")


            db_transcription_segments: list[TranscriptionSegmentDb] = []

            for segment in transcription_segments:
                segment_db = TranscriptionSegmentDb(
                    id=str(uuid4()),
                    audio_file_id=audio_file_id,
                    no=segment.no,
                    start=segment.start,
                    end=segment.end,
                    text=segment.text
                )
                insert_transcription_segment(cursor, segment_db)
                db_transcription_segments.append(segment_db)

            conn.commit()

            available_ads = get_advertisements(cursor)

            ad_placements = determine_ad_placement(transcription_segments, available_ads)

            print(f"Possible Ad Placements: {ad_placements}")

            for ad_placement in ad_placements:
                generated_advertisement_texts = generate_advertisements(ad_placement, transcription_segments)
                print(f"Generated Advertisement Texts: {generated_advertisement_texts}")

                for generated_advertisement_text in generated_advertisement_texts:
                    base_text = generated_advertisement_text.segue + " " + generated_advertisement_text.content + " " + generated_advertisement_text.exit
                    voice_id = determine_optimal_voice_id(base_text, db_transcription_segments, ad_placement)
                    if voice_id == "default":
                        advertisement_audio_path = generate_advertisement_audio(base_text)
                    else:
                        advertisement_audio_path = generate_advertisement_audio(base_text, voice_id)
                    with open(advertisement_audio_path, "rb") as f:
                        advertisement_audio_bytes = f.read()
                    os.remove(advertisement_audio_path)

                    segment_db = next(s for s in db_transcription_segments if s.no == ad_placement.transcription_segment.no)
                    transcription_segment_id = segment_db.id

                    generated_ad = GeneratedAd(
                        id=str(uuid4()),
                        segue=generated_advertisement_text.segue,
                        content=generated_advertisement_text.content,
                        exit=generated_advertisement_text.exit,
                        audio_bytes=advertisement_audio_bytes,
                        audio_file_id=audio_file_id,
                        processing_status=ProcessingStatus.COMPLETE,
                        transcription_segment_id=transcription_segment_id,
                        advertisement_id=ad_placement.determined_advertisement.id
                    )
                    insert_generated_ad(cursor, generated_ad)

                    conn.commit()

            update_audio_status(cursor, audio_file_id, ProcessingStatus.COMPLETE)
            conn.commit()

            print(f"Completed processing for audio file {audio_file_id}")
    except Exception as e:
        import traceback
        print(f"Error processing audio file {audio_file_id}: {str(e)}")
        print(f"Traceback:\n{traceback.format_exc()}")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            update_audio_status(cursor, audio_file_id, ProcessingStatus.FAILED)
            conn.commit()

def stitch_advertisements_into_audio_file(audio_file_id: str, generated_ad_id: str, stitched_audio_id: str):
    print(f"Stitching advertisements into audio file {audio_file_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            update_stitched_audio_status(cursor, stitched_audio_id, ProcessingStatus.PROCESSING)
            conn.commit()

            audio_file = get_audio_file_by_id(cursor, audio_file_id)
            generated_ad = get_generated_ad_by_id(cursor, generated_ad_id)

            if not audio_file or not generated_ad:
                raise ValueError("Audio file or generated ad not found")
            
            if generated_ad.processing_status != ProcessingStatus.COMPLETE:
                raise ValueError("Generated ad is not complete")
            
            if generated_ad.audio_bytes is None:
                raise ValueError("Generated ad audio bytes are not available")
            
            if audio_file.bytes is None:
                raise ValueError("Audio file bytes are not available")
            
            transcription_segment = get_transcription_segment_by_id(cursor, generated_ad.transcription_segment_id)

            if not transcription_segment:
                raise ValueError("Transcription segment not found")
            
            print(f"Stitching advertisement into audio file {audio_file_id} after segment {transcription_segment.no}")
            output_path = insert_advertisement_audio(audio_file.bytes, generated_ad.audio_bytes, transcription_segment)

            print(f"Stitched advertisement into audio file {audio_file_id} at {output_path}")

            stitched_audio_bytes = open(output_path, "rb").read()
            os.remove(output_path)

            update_stitched_audio_bytes(cursor, stitched_audio_id, stitched_audio_bytes)

            conn.commit()
            
            update_stitched_audio_status(cursor, stitched_audio_id, ProcessingStatus.COMPLETE)
            conn.commit()
            
            print(f"Completed stitching advertisements into audio file {audio_file_id}")
            
    except Exception as e:
        import traceback
        print(f"Error stitching advertisements into audio file {audio_file_id}: {str(e)}")
        print(f"Traceback:\n{traceback.format_exc()}")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            update_stitched_audio_status(cursor, stitched_audio_id, ProcessingStatus.FAILED)
            conn.commit()
            
def produce_ad_audio_with_nearby_audio(generated_ad: GeneratedAd):
    if generated_ad.id in _ad_audio_cache:
        return _ad_audio_cache[generated_ad.id]

    if generated_ad.audio_bytes is None:
        raise ValueError("Generated ad audio bytes are not available")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        transcription_segment = get_transcription_segment_by_id(cursor, generated_ad.transcription_segment_id)
        if not transcription_segment:
            raise ValueError("Transcription segment not found")
        
        audio_file = get_audio_file_by_id(cursor, generated_ad.audio_file_id)
        if not audio_file:
            raise ValueError("Audio file not found")
        
        ad_audio_with_nearby_audio = generate_ad_audio_with_nearby_audio(generated_ad.audio_bytes, transcription_segment, audio_file.bytes)
        _ad_audio_cache[generated_ad.id] = ad_audio_with_nearby_audio
        
        return ad_audio_with_nearby_audio
        
        
    