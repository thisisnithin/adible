import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from pydub import AudioSegment
import json
from uuid import uuid4

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=OPENAI_API_KEY
)

class TranscriptionSegment(BaseModel):
    start: float
    end: float
    text: str

def transcribe_audio_with_timestamps(file_path: str, audio_id: str):
    print(f"Starting transcription for file: {file_path}")
    audio = AudioSegment.from_file(file_path)
    
    segment_duration = 2 * 60 * 1000
    print(f"Processing audio in {segment_duration/1000} second segments")
    
    transcription_segments = []
    total_time_processed = 0  # Initialize total time processed
    
    for i in range(0, len(audio), segment_duration):
        print(f"Processing segment {i // segment_duration + 1}")
        segment = audio[i:i + segment_duration]
        
        segment_file_path = f"temp_segment_{i // segment_duration}.mp3"
        segment.export(segment_file_path, format="mp3")
        print(f"Exported segment to {segment_file_path}")
        
        with open(segment_file_path, 'rb') as audio_file:
            print("Sending segment to OpenAI for transcription...")
            transcription_verbose = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
        
        for t_segment in transcription_verbose.segments:
            start_time = total_time_processed + t_segment.start
            end_time = total_time_processed + t_segment.end
            print(f"Segment from {start_time} to {end_time}: {t_segment.text}")

            transcription_segments.append({
                "start": start_time,
                "end": end_time,
                "text": t_segment.text
            })
        
        total_time_processed += len(segment)
        print(f"Total time processed: {total_time_processed / 1000} seconds")  # Print total time processed in seconds

    print("Saving transcription data to file...")
    transcription_data = {
        "transcriptions": {
            "id": audio_id,
            "segments": transcription_segments
        }
    }
    
    with open("transcription_state.json", "w") as f:
        json.dump(transcription_data, f, indent=4)

    print("Transcription complete!")
    return transcription_segments


transcribe_audio_with_timestamps("/Users/pradyumnarahulk/Downloads/demo/rogan_chess_preparation_w_magnus.mp3", str(uuid4()))


