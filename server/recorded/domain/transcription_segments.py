
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel
from sqlite3 import Cursor


class TranscriptionSegmentDb(BaseModel):
    id: Optional[str] = str(uuid4())
    audio_file_id: str
    no: int
    start: float
    end: float
    text: str

def row_to_transcription_segment(row) -> TranscriptionSegmentDb:
    return TranscriptionSegmentDb(
        id=row['id'],
        audio_file_id=row['audio_file_id'],
        no=row['no'],
        start=row['start'],
        end=row['end'],
        text=row['text']
    )

def insert_transcription_segment(cursor: Cursor, segment: TranscriptionSegmentDb) -> int:
    query = """
    INSERT INTO transcription_segments (id, audio_file_id, no, start, end, text)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (segment.id, segment.audio_file_id, segment.no, 
                          segment.start, segment.end, segment.text))
    return cursor.lastrowid

def get_transcription_segments(cursor: Cursor, audio_file_id: str) -> list[TranscriptionSegmentDb]:
    query = "SELECT * FROM transcription_segments WHERE audio_file_id = ?"
    rows = cursor.execute(query, (audio_file_id,)).fetchall()
    return [row_to_transcription_segment(row) for row in rows]