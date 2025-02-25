import json

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.background import BackgroundTasks

from rt_convo.models.get_ad_model import GetAdResp, GetAdReq
from rt_convo.models.should_show_ad_model import ShouldShowAdResp, ShouldShowAdReq
from server.rt_convo.models.get_ad_model import GetAdByIdResp
from server.services.qdrant_helpers import similarity_search, get_by_id
from services.oai import oai_complete_structured
from rt_convo.prompts import SHOULD_SHOW_AD_SYS_PROMPT, GENERATE_AD_SYS_PROMPT
from services.g_sheets import load_sheet_data
from services.qdrant_helpers import index_data

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

@app.post("/rt_ads/v2/get_ad/",response_model=GetAdResp)
def get_ad(
        get_ad_req: GetAdReq
):
    print(get_ad_req)
    # TODO: Vec/text search this from sheets.

    data = similarity_search(get_ad_req.conversation_context + " \n " + get_ad_req.raw_transcription_text)
    ai_parse_resp: GetAdResp = oai_complete_structured(
        query=get_ad_req.model_dump_json(),
        sys_prompt=GENERATE_AD_SYS_PROMPT.format(advert_info=data.response),
        response_model=GetAdResp
    )
    resp = GetAdResp(
        response_rewrite_instructions=ai_parse_resp.response_rewrite_instructions,
        # intro_sfx=ai_parse_resp.intro_sfx # TODO: add sfx as a tool somehow.
        source_ids = [src.metadata["url"] for src in data.source_nodes]
    )
    return resp

@app.post("/rt_ads/v2/get_ad_by_id/{doc_id}",response_model=GetAdByIdResp)
def get_ad_by_id(
        doc_id: str
):
    docs = get_by_id(doc_id)
    print(docs)
    return GetAdByIdResp(urls=[d.payload["url"] for d in docs])


@app.post("/test/search")
def search():
    query = "I want to buy a car"
    doc = similarity_search(query)
    try:
        source =doc.source_nodes[0].metadata["url"] or "https://dominos.com"
    except Exception as e:
        source = "https://dominos.com"
        print(e)
    return {"response": doc.response, "source": source}

@app.post("/rt_ads/reindex")
async def reindex_ads(background_tasks: BackgroundTasks):
    sheet_data = load_sheet_data()
    # index
    # index_data(rows = sheet_data[1:]) # Skip the header row
    background_tasks.add_task(index_data, sheet_data[1:], "adible")
    return {"message": "Reindexed RT Ads from the Google Sheet on the server."}


if __name__ == "__main__":
    load_dotenv("server/.env")
    uvicorn.run(app, host="0.0.0.0", port=3000)
