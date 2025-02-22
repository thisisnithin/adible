from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import uvicorn
import uuid
import os

from db import get_db_connection
from domain.audio_file import AudioFile, insert_audio_file
from domain.common import ProcessingStatus

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str = None

class ResponseModel(BaseModel):
    message: str
    item: Item

@app.post("/items/", response_model=ResponseModel)
async def create_item(item: Item):
    return ResponseModel(message="Item received", item=item)

@app.post("/upload-audio/", status_code=201)
async def upload_audio(file: UploadFile = File(...)):
    file_bytes = await file.read()
    
    audio_file = AudioFile(
        file_name=file.filename,
        bytes=file_bytes,
        processing_status=ProcessingStatus.PENDING
    )
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        insert_audio_file(cursor, audio_file)
        conn.commit()
    
    return {"id": audio_file.id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4001)
