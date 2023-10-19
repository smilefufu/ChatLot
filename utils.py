"""工具函数集"""
import re
import json


def extract_json_from_markdown(markdown_text):
    pattern = r'```json([\s\S]*?)```'
    json_list = []

    matches = re.findall(pattern, markdown_text)
    for match in matches:
        try:
            json_data = json.loads(match.strip())
            json_list.append(json_data)
        except json.JSONDecodeError:
            print("Invalid JSON detected.")

    return json_list
