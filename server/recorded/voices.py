
from pydantic import BaseModel


class Voice(BaseModel):
    id: str
    description: str
    language: str

AVAILABLE_VOICES = [
    Voice(id="WTUK291rZZ9CLPCiFTfh", description="A well-connected, young conversational male that's perfect for podcasting or casual conversations.", language="English"),
    Voice(id="mhgBlD8CmCSdwLDOIJpA", description="Sharp, modern, conversational, and fast-paced, viral-ready news updates with urgency and bite", language="English"),
    Voice(id="7H4vk4UjjbKDZiGTgH8K", description="A smooth yet assertive middle aged female voice great for a variety of projects including news, social media, conversational, audiobooks, and instructional videos.", language="English"),
    Voice(id="IvLWq57RKibBrqZGpQrC", description="An energetic Hindi lively voice with standard accent. The voice brimming with energy,", language="Hindi"),
]