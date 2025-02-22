from sqlite3 import Cursor
from typing import Optional
from uuid import uuid4
from pydantic import BaseModel

from domain.common import ProcessingStatus

class GeneratedAd(BaseModel):
    id: Optional[str] = str(uuid4())
    segue: str
    content: str
    exit: str
    audio_bytes: bytes
    audio_file_id: str
    processing_status: ProcessingStatus
    transcription_segment_id: str

def row_to_generated_ad(row) -> GeneratedAd:
    return GeneratedAd(
        id=row['id'],
        segue=row['segue'],
        content=row['content'],
        exit=row['exit'],
        audio_bytes=row['audio_bytes'],
        audio_file_id=row['audio_file_id'],
        processing_status=ProcessingStatus(row['processing_status']),
        transcription_segment_id=row['transcription_segment_id']
    )

def insert_generated_ad(cursor: Cursor, ad: GeneratedAd) -> int:
    query = """
    INSERT INTO generated_ads (id, segue, content, exit, audio_bytes, audio_file_id, processing_status, transcription_segment_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (ad.id, ad.segue, ad.content, ad.exit, ad.audio_bytes, 
                          ad.audio_file_id, ad.processing_status, ad.transcription_segment_id))
    return cursor.lastrowid

def update_ad_status(cursor: Cursor, ad_id: int, status: ProcessingStatus):
    query = "UPDATE generated_ads SET processing_status = ? WHERE id = ?"
    cursor.execute(query, (status, ad_id))

def get_generated_ads(cursor: Cursor) -> list[GeneratedAd]:
    query = "SELECT * FROM generated_ads"
    rows = cursor.execute(query).fetchall()
    return [row_to_generated_ad(row) for row in rows]

def get_generated_ads_by_segment_id(cursor: Cursor, segment_id: str) -> list[GeneratedAd]:
    query = "SELECT * FROM generated_ads WHERE transcription_segment_id = ?"
    rows = cursor.execute(query, (segment_id,)).fetchall()
    return [row_to_generated_ad(row) for row in rows]

def get_generated_ads_by_audio_file_id(cursor: Cursor, audio_file_id: str) -> list[GeneratedAd]:
    query = "SELECT * FROM generated_ads WHERE audio_file_id = ?"
    rows = cursor.execute(query, (audio_file_id,)).fetchall() 
    return [row_to_generated_ad(row) for row in rows]

def get_generated_ad_by_id(cursor: Cursor, ad_id: str) -> GeneratedAd:
    query = "SELECT * FROM generated_ads WHERE id = ?"
    row = cursor.execute(query, (ad_id,)).fetchone()
    return row_to_generated_ad(row) if row else None
