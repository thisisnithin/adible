from sqlite3 import Cursor
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel

from domain.common import ProcessingStatus

class StitchedAudio(BaseModel):
    id: Optional[str] = str(uuid4())
    audio_file_id: str
    generated_ad_id: str
    audio_bytes: Optional[bytes] = None
    processing_status: ProcessingStatus

def row_to_stitched_audio(row) -> StitchedAudio:
    return StitchedAudio(
        id=row['id'],
        audio_file_id=row['audio_file_id'],
        generated_ad_id=row['generated_ad_id'],
        audio_bytes=row['audio_bytes'],
        processing_status=ProcessingStatus(row['processing_status'])
    )

def insert_stitched_audio(cursor: Cursor, audio: StitchedAudio) -> str:
    query = """
    INSERT INTO stitched_audio (id, audio_file_id, generated_ad_id, audio_bytes, processing_status)
    VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(query, (audio.id, audio.audio_file_id, audio.generated_ad_id, 
                          audio.audio_bytes, audio.processing_status))
    return cursor.lastrowid

def update_stitched_audio_status(cursor: Cursor, audio_id: int, status: ProcessingStatus):
    query = "UPDATE stitched_audio SET processing_status = ? WHERE id = ?"
    cursor.execute(query, (status, audio_id))

def get_stitched_audios(cursor: Cursor) -> list[StitchedAudio]:
    query = "SELECT * FROM stitched_audio"
    rows = cursor.execute(query).fetchall()
    return [row_to_stitched_audio(row) for row in rows]

def update_stitched_audio_bytes(cursor: Cursor, audio_id: str, bytes: bytes):
    query = "UPDATE stitched_audio SET audio_bytes = ? WHERE id = ?"
    cursor.execute(query, (bytes, audio_id))

def get_stitched_audio_by_id(cursor: Cursor, audio_id: str) -> StitchedAudio:
    query = "SELECT * FROM stitched_audio WHERE id = ?"
    row = cursor.execute(query, (audio_id,)).fetchone()
    return row_to_stitched_audio(row) if row else None
