from sqlite3 import Cursor
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel

from server.recorded.domain.common import ProcessingStatus

class StitchedAudio(BaseModel):
    id: Optional[str] = str(uuid4())
    audio_file_id: str
    generated_ad_id: str
    bytes: bytes
    processing_status: ProcessingStatus

def row_to_stitched_audio(row) -> StitchedAudio:
    return StitchedAudio(
        id=row['id'],
        audio_file_id=row['audio_file_id'],
        generated_ad_id=row['generated_ad_id'],
        bytes=row['bytes'],
        processing_status=ProcessingStatus(row['processing_status'])
    )

def insert_stitched_audio(cursor: Cursor, audio: StitchedAudio) -> int:
    query = """
    INSERT INTO stitched_audio (id, audio_file_id, generated_ad_id, bytes, processing_status)
    VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(query, (audio.id, audio.audio_file_id, audio.generated_ad_id, 
                          audio.bytes, audio.processing_status))
    return cursor.lastrowid

def update_stitched_audio_status(cursor: Cursor, audio_id: int, status: ProcessingStatus):
    query = "UPDATE stitched_audio SET processing_status = ? WHERE id = ?"
    cursor.execute(query, (status, audio_id))

def get_stitched_audios(cursor: Cursor) -> list[StitchedAudio]:
    query = "SELECT * FROM stitched_audio"
    rows = cursor.execute(query).fetchall()
    return [row_to_stitched_audio(row) for row in rows]
