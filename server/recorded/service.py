import os
from tempfile import NamedTemporaryFile
from uuid import uuid4
from domain.audio_file import get_audio_file_by_id, update_audio_status
from db import get_db_connection

from interface import determine_ad_placement, generate_advertisement_audio, generate_advertisements, transcribe_audio_with_timestamps
from domain.transcription_segments import TranscriptionSegmentDb, insert_transcription_segment
from domain.common import ProcessingStatus
from domain.generated_ad import GeneratedAd, insert_generated_ad

def process_audio_file_and_generate_advertisements(audio_file_id: str):
    print(f"Starting processing for audio file {audio_file_id}")
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
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

            ad_placements = determine_ad_placement(transcription_segments)

            print(f"Possible Ad Placements: {ad_placements}")

            for ad_placement in ad_placements:
                generated_advertisement_texts = generate_advertisements(ad_placement, transcription_segments)
                print(f"Generated Advertisement Texts: {generated_advertisement_texts}")

                for generated_advertisement_text in generated_advertisement_texts:
                    advertisement_audio_path = generate_advertisement_audio(generated_advertisement_text.segue + " " + generated_advertisement_text.content + " " + generated_advertisement_text.exit)
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
                        transcription_segment_id=transcription_segment_id
                    )
                    insert_generated_ad(cursor, generated_ad)

                    conn.commit()

            update_audio_status(cursor, audio_file_id, ProcessingStatus.COMPLETE)
            conn.commit()

            print(f"Completed processing for audio file {audio_file_id}")
    except Exception as e:
        print(f"Error processing audio file {audio_file_id}: {str(e)}")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            update_audio_status(cursor, audio_file_id, ProcessingStatus.FAILED)
            conn.commit()
