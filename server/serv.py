import json

from fastapi import FastAPI

from rt_convo.models.get_ad_model import GetAdResp, GetAdReq
from rt_convo.models.should_show_ad_model import ShouldShowAdResp, ShouldShowAdReq
from rt_convo.oai import oai_complete_structured
from rt_convo.prompts import SHOULD_SHOW_AD_SYS_PROMPT, GENERATE_AD_SYS_PROMPT
from rt_convo.g_sheets import load_sheet_data

app = FastAPI(
    debug=True,
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/rt_ads")
def gen_rt_ads():
    return {"message": "Generates RT Ads"}

@app.post("/rt_ads/should_show_ad",response_model=ShouldShowAdResp)
def should_show_ad(
    should_show_ad_req: ShouldShowAdReq
):
    print(should_show_ad_req)
    if should_show_ad_req.open_mindedness > 5:
    # Check if the user is open to ads
        ai_parse_resp: ShouldShowAdResp = oai_complete_structured(
            query=should_show_ad_req.model_dump_json(),
            sys_prompt=SHOULD_SHOW_AD_SYS_PROMPT,
            response_model= ShouldShowAdResp
        )

        resp = ShouldShowAdResp(
            should_show_ad= ai_parse_resp.should_show_ad,
            relevant_keywords_for_available_ads= ai_parse_resp.relevant_keywords_for_available_ads
        )
    else:
        resp = ShouldShowAdResp(should_show_ad = False, relevant_keywords_for_available_ads=[])
    return resp

@app.post("/rt_ads/get_ad",response_model=GetAdResp)
def get_ad(
        get_ad_req: GetAdReq
):
    print(get_ad_req)
    # TODO: Vec/text search this from sheets.

    sheet_data = json.dumps(load_sheet_data())
    ai_parse_resp: GetAdResp = oai_complete_structured(
        query=get_ad_req.model_dump_json(),
        sys_prompt=GENERATE_AD_SYS_PROMPT.format(advert_info=sheet_data),
        response_model=GetAdResp
    )
    resp = GetAdResp(
        response_rewrite_instructions=ai_parse_resp.response_rewrite_instructions,
        intro_sfx=ai_parse_resp.intro_sfx # TODO: add sfx as a tool somehow.
    )
    return resp

