from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from pydantic import BaseModel
import uvicorn

from db import get_db_connection
from domain.audio_file import AudioFile, insert_audio_file, get_audio_file_by_id
from domain.common import ProcessingStatus
from service import process_audio_file_and_generate_advertisements

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str = None

class ResponseModel(BaseModel):
    message: str
    item: Item

@app.post("/items", response_model=ResponseModel)
async def create_item(item: Item):
    return ResponseModel(message="Item received", item=item)

@app.post("/upload-audio", status_code=201)
async def upload_audio(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    print(f"Received audio upload request for file: {file.filename}")
    file_bytes = await file.read()
    
    audio_file = AudioFile(
        file_name=file.filename,
        bytes=file_bytes,
        processing_status=ProcessingStatus.PENDING
    )
    print(f"Created AudioFile object with ID: {audio_file.id}")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            insert_audio_file(cursor, audio_file)
            conn.commit()
            print(f"Successfully saved audio file to database: {audio_file.id}")
    except Exception as e:
        print(f"Error saving to database: {str(e)}")
        raise
    
    background_tasks.add_task(process_audio_file_and_generate_advertisements, audio_file.id)
    print(f"Added background task for processing audio file: {audio_file.id}")
    
    return {"id": audio_file.id}

@app.get("/audio/{file_id}")
async def get_audio(file_id: str):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            audio_file = get_audio_file_by_id(cursor, file_id)
            
            if not audio_file:
                return {"error": "Audio file not found"}, 404
                
            return {
                "id": audio_file.id,
                "file_name": audio_file.file_name,
                "processing_status": audio_file.processing_status
            }
    except Exception as e:
        print(f"Error fetching audio file: {str(e)}")
        raise

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=4001, reload=True)
