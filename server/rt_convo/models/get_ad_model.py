from typing import List

from pydantic import BaseModel


class GetAdReq(BaseModel):
    open_mindedness: float
    conversation_context: str
    raw_transcription_text: str
    potential_receptive_topics: List[str]


class GetAdResp(BaseModel):
    response_rewrite_instructions: str
    intro_sfx: str

