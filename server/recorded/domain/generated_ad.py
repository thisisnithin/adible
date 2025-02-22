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

def row_to_generated_ad(row) -> GeneratedAd:
    return GeneratedAd(
        id=row['id'],
        segue=row['segue'],
        content=row['content'],
        exit=row['exit'],
        audio_bytes=row['audio_bytes'],
        audio_file_id=row['audio_file_id'],
        processing_status=ProcessingStatus(row['processing_status'])
    )

def insert_generated_ad(cursor: Cursor, ad: GeneratedAd) -> int:
    query = """
    INSERT INTO generated_ads (id, segue, content, exit, audio_bytes, audio_file_id, processing_status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (ad.id, ad.segue, ad.content, ad.exit, ad.audio_bytes, 
                          ad.audio_file_id, ad.processing_status))
    return cursor.lastrowid

def update_ad_status(cursor: Cursor, ad_id: int, status: ProcessingStatus):
    query = "UPDATE generated_ads SET processing_status = ? WHERE id = ?"
    cursor.execute(query, (status, ad_id))

def get_generated_ads(cursor: Cursor) -> list[GeneratedAd]:
    query = "SELECT * FROM generated_ads"
    rows = cursor.execute(query).fetchall()
    return [row_to_generated_ad(row) for row in rows]
