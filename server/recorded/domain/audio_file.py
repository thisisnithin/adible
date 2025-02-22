from typing import Optional
from uuid import uuid4
from sqlite3 import Cursor
from pydantic import BaseModel

from domain.common import ProcessingStatus

class AudioFile(BaseModel):
    id: Optional[str] = str(uuid4())
    file_name: str
    bytes: bytes
    processing_status: ProcessingStatus

def row_to_audio_file(row) -> AudioFile:
    return AudioFile(
        id=row['id'],
        file_name=row['file_name'],
        bytes=row['bytes'],
        processing_status=ProcessingStatus(row['processing_status'])
    )

def insert_audio_file(cursor: Cursor, audio_file: AudioFile) -> int:
    query = """
    INSERT INTO audio_files (id, file_name, bytes, processing_status)
    VALUES (?, ?, ?, ?)
    """
    cursor.execute(query, (audio_file.id, audio_file.file_name, audio_file.bytes, audio_file.processing_status))
    return cursor.lastrowid

def update_audio_status(cursor: Cursor, file_id: int, status: ProcessingStatus):
    query = "UPDATE audio_files SET processing_status = ? WHERE id = ?"
    cursor.execute(query, (status.value, file_id))

def get_audio_files(cursor: Cursor) -> list[AudioFile]:
    query = "SELECT * FROM audio_files"
    rows = cursor.execute(query).fetchall()
    return [row_to_audio_file(row) for row in rows]

def get_audio_file_by_id(cursor: Cursor, file_id: str) -> Optional[AudioFile]:
    query = "SELECT * FROM audio_files WHERE id = ?"
    row = cursor.execute(query, (file_id,)).fetchone()
    return row_to_audio_file(row) if row else None
