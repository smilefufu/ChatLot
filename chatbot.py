"""聊天bot类"""
import os
import time
import json
import urllib.parse

from dotenv import load_dotenv
import aiohttp
import requests

import prompts

load_dotenv()
API_KEY = os.getenv("AK")
SECRET_KEY = os.getenv("SK")


class LLMBot:
    """聊天机器人"""
    def __init__(self, api_key=None, secret_key=None, llm_config=None):
        self.api_key = api_key or API_KEY
        self.secret_key = secret_key or SECRET_KEY
        self.llm_config = llm_config or {}

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
            prompt = prompts.MED_PROMPT_SURGERY.format(question=question, columns=columns, surg="、".join(extra), len_surg=len(extra))
        else:
            prompt = prompts.MED_PROMPT.format(question=question, group_name=group_name, columns=columns)
        return await self.async_chat(prompt)


if __name__ == "__main__":
    bot = LLMBot()
    print(bot.ask_monthly_attendance("出勤率最低的部门是哪五个部门？"))
    # with open("info.txt", "r", encoding="utf-8") as f:
    #     for line in f.readlines():
    #         print(line, "\n")
    #         print(bot.ask_med(line).replace("\n\n", "\n"))
    #         print("\n\n===========================\n\n")
    #         break
