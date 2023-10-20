"""聊天bot类"""
import os
import time
import json
import logging

from dotenv import load_dotenv
import aiohttp
import requests

import prompts
from utils import extract_json_from_markdown

load_dotenv()
API_KEY = os.getenv("AK")
SECRET_KEY = os.getenv("SK")

CACHE = {}

class LLMBot:
    """聊天机器人"""
    def __init__(self, api_key=None, secret_key=None, llm_config=None):
        self.api_key = api_key or API_KEY
        self.secret_key = secret_key or SECRET_KEY
        self.llm_config = llm_config or {"top_p": 0, "temperature": 0.01}

    def async_request(self, url, data=None, method="POST"):
        """异步请求"""
        async def _request():
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, data=data) as resp:
                    return await resp.json()

        return _request()

    def sync_request(self, url, data=None, method="POST"):
        """同步请求"""
        resp = requests.request(method, url, data=data, timeout=60)
        return resp.json()

    def get_access_token(self):
        """鉴权"""
        # 先取环境变量已经拿到的auth
        auth = os.getenv("QIANFAN_AUTH")
        if auth:
            expire = os.getenv("QIANFAN_AUTH_EXPIRE")
            if expire and float(expire) > time.time():
                return auth
        url = f"https://aip.baidubce.com/oauth/2.0/token?client_id={self.api_key}&client_secret={self.secret_key}&grant_type=client_credentials"
        resp = self.sync_request(url)
        auth = resp.get("access_token")
        if auth:
            expire = resp.get("expires_in") + time.time()
            # 保存到环境变量
            os.environ["QIANFAN_AUTH"] = auth
            os.environ["QIANFAN_AUTH_EXPIRE"] = str(expire)
            return auth

    def chat(self, question, history=None):
        """聊天"""
        if not history:
            history = []
        history.append({"role": "user", "content": question})
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token=" + self.get_access_token()
        payload = {"messages": history, **self.llm_config}
        resp = self.sync_request(url, method="POST", data=json.dumps(payload))
        return resp["result"]
    
    async def async_chat(self, question, history=None):
        """聊天"""
        if not history:
            history = []
        history.append({"role": "user", "content": question})
        url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token=" + self.get_access_token()
        payload = {"messages": history, **self.llm_config}
        resp = await self.async_request(url, method="POST", data=json.dumps(payload))
        logging.info(resp)
        return resp["result"]
    
    def ask_monthly_attendance(self, question):
        """月度考勤"""
        prompt = prompts.MONTH_ATTENDANCE_PROMPT.format(question)
        print(prompt)
        return self.chat(prompt)
    
    async def ask_med(self, question):
        # 废弃
        result = {}
        for group_name, columns in prompts.MED_COLUMNS.items():
            prompt = prompts.MED_PROMPT.format(question=question, group_name=group_name, columns=columns)
            result[group_name] = await self.async_chat(prompt)
        return result
    
    async def ask_med_catetory(self, category, question, extra=None):
        group_name = category
        columns = prompts.MED_COLUMNS[group_name]
        if group_name == "手术操作":
            # 先区分出手术来
            result = []
            prompt = prompts.MED_PROMPT_SURGERY_DISTINCT.format(question=question, columns=columns, surg="、".join(extra), len_surg=len(extra))
            r = await self.async_chat(prompt)
            json_result = extract_json_from_markdown(r)
            json_result = json_result[0] if json_result else []
            logging.info(json_result)
            for surgery in json_result:
                surgery_name = surgery["手术名称"]
                surgery_text = surgery["描述"]
                # prompt = prompts.MED_PROMPT_SURGERY.format(question=question, columns=columns, surg="、".join(extra), len_surg=len(extra))
                prompt = prompts.MED_PROMPT_SURGERY2.format(text=surgery_text, surgery_name=surgery_name)
                logging.info(prompt)
                r = await self.async_chat(prompt)
                json_result = extract_json_from_markdown(r)
                logging.info("找到json result：%s", json_result)
                if json_result:
                    result.append(json_result[0])
            return result
        elif group_name == "药品表":
            prompt = prompts.MED_PROMPT_MEDICINE_PRE.format(question=question, columns=columns)
            logging.info(prompt)
        else:
            prompt = prompts.MED_PROMPT.format(question=question, group_name=group_name, columns=columns)
        # self.llm_config["system"] = "你是一名病历分析助手，根据用户提供的病历和要求分析的字段，提取实体词到json中。要求分析的字段中，如有未在病历中提及的，则不必提取。"
        answer = await self.async_chat(prompt)
        json_list = extract_json_from_markdown(answer)
        result = json_list[0] if json_list else []
        return result
    
    async def ask_med_knowledge(self, med_name, context):
        prompt = f"结合语境`{context}`告诉我这些药品：`{'、'.join(med_name)}`的活性成分、通用名、商品名、药品分类、药物剂型这五个字段。如果字段中存在未知或你不确定的字段，一律返回空，以json的形式回答，json的key是药品名称，value是对应的五个字段的对象。"
        answer = await self.async_chat(prompt)
        json_list = extract_json_from_markdown(answer)
        result = json_list[0] if json_list else []
        return result


if __name__ == "__main__":
    bot = LLMBot()
    print(bot.ask_monthly_attendance("出勤率最低的部门是哪五个部门？"))
    # with open("info.txt", "r", encoding="utf-8") as f:
    #     for line in f.readlines():
    #         print(line, "\n")
    #         print(bot.ask_med(line).replace("\n\n", "\n"))
    #         print("\n\n===========================\n\n")
    #         break
