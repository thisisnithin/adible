import os
from tempfile import NamedTemporaryFile
from uuid import uuid4
from domain.audio_file import get_audio_file_by_id, update_audio_status
from db import get_db_connection

from interface import transcribe_audio_with_timestamps
from domain.transcription_segments import TranscriptionSegmentDb, insert_transcription_segment
from domain.common import ProcessingStatus

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
            transcription_segments = transcribe_audio_with_timestamps(temp_file_path, audio_file_id)
            print(f"Received {len(transcription_segments)} segments for {audio_file_id}")

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
            
            update_audio_status(cursor, audio_file_id, ProcessingStatus.COMPLETE)

            conn.commit()
            print(f"Completed processing for audio file {audio_file_id}")
    except Exception as e:
        print(f"Error processing audio file {audio_file_id}: {str(e)}")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            update_audio_status(cursor, audio_file_id, ProcessingStatus.FAILED)
            conn.commit()
