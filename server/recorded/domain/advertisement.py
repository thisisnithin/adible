from typing import Optional, List
from uuid import uuid4
from pydantic import BaseModel
from sqlite3 import Cursor

class AdvertisementDb(BaseModel):
    id: Optional[str] = str(uuid4())
    url: str
    title: str 
    content: str
    tags: List[str]

def row_to_advertisement(row) -> AdvertisementDb:
    return AdvertisementDb(
        id=row['id'],
        url=row['url'],
        title=row['title'],
        content=row['content'],
        tags=row['tags'].split(',') if row['tags'] else []
    )

def insert_advertisement(cursor: Cursor, ad: AdvertisementDb) -> int:
    query = """
    INSERT INTO advertisements (id, url, title, content, tags)
    VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(query, (ad.id, ad.url, ad.title, ad.content, 
                          ','.join(ad.tags)))
    return cursor.lastrowid

def get_advertisement_by_id(cursor: Cursor, ad_id: str) -> AdvertisementDb:
    query = "SELECT * FROM advertisements WHERE id = ?"
    row = cursor.execute(query, (ad_id,)).fetchone()
    return row_to_advertisement(row) if row else None

def get_advertisements(cursor: Cursor) -> list[AdvertisementDb]:
    query = "SELECT * FROM advertisements"
    rows = cursor.execute(query).fetchall()
    return [row_to_advertisement(row) for row in rows]
