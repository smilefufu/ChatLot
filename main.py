
import traceback
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from chatbot import LLMBot
from utils import extract_json_from_markdown


logging.basicConfig(
    format='[%(levelname)s %(asctime)s %(funcName)s(%(filename)s:%(lineno)s)] %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S', level=logging.INFO)
app = FastAPI()


class Query(BaseModel):
    text: str       # 手术操作、病理检查、淋巴结病理、药品表、分子病理和免疫组化
    category: str
    extra: list


@app.post("/llm_relation_extract/")
async def ask_med_endpoint(query: Query):
    try:
        llm_bot = LLMBot()
        # answers = await llm_bot.ask_med(query.text)
        # result = {}
        # for key, answer in answers.items():
        #     json_list = extract_json_from_markdown(answer)
        #     result[key] = json_list[0] if json_list else None
        # return {"result": result}
        result = await llm_bot.ask_med_catetory(query.category, query.text, query.extra)
        if query.category == "手术操作":
            for r in result:
                for k, v in list(r.items()):
                    if v == "未知" or v == [] or v == "":
                        del r[k]
        return {"result": result}
    except Exception as e:
        logging.info(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e)) from e
