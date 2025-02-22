from typing import List

from pydantic import BaseModel


class ShouldShowAdReq(BaseModel):
    open_mindedness: float
    potential_receptive_topic: str
    conversation_context: str


class ShouldShowAdResp(BaseModel):
    should_show_ad: bool
    relevant_keywords_for_available_ads: List[str]
