from typing import List, Optional

from pydantic import BaseModel


class GetAdReq(BaseModel):
    open_mindedness: float
    conversation_context: str
    raw_transcription_text: str
    potential_receptive_topics: List[str]


class GetAdResp(BaseModel):
    response_rewrite_instructions: str
    intro_sfx: Optional[str]
    # source_ids: Optional[List[str]]


class GetAdByIdReq(BaseModel):
    source_id: str

class GetAdByIdResp(BaseModel):
    urls: List[str]