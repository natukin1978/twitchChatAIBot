import json
import twitchio
from typing import Any, Dict
import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold, HarmCategory

import global_value as g
from text_helper import readText


class GenAI:
    GENAI_SAFETY_SETTINGS = {
        # ハラスメントは中程度を許容する
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        # ヘイトスピーチは厳しく制限する
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        # セクシャルな内容を多少は許容する
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        # ゲーム向けなので、危険に分類されるコンテンツを許容できる
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    def __init__(self, config):
        conf_g = config["google"]
        genai.configure(api_key=conf_g["geminiApiKey"])
        genaiModel = genai.GenerativeModel(conf_g["modelName"])
        self.genaiChat = genaiModel.start_chat(history=[])

    @staticmethod
    def create_message_json(msg: twitchio.Message) -> Dict[str, Any]:
        return {
            "id": msg.author.name,
            "displayName": msg.author.display_name,
            "content": None,  # 関数外で設定してね
            "isFirst": msg.first,
            "answerLength": 40,
            "answerLevel": 1,  # `質問や問いかけに答える`か、`傍観する`かを、あなたの判断に任せます
        }

    def send_message(self, message: str) -> str:
        try:
            print(message)
            response = self.genaiChat.send_message(
                message, safety_settings=self.GENAI_SAFETY_SETTINGS
            )
            print(response.text)
            return response.text
        except Exception as e:
            print(e)
            return g.ERROR_MESSAGE

    def send_message_by_json(self, json_data: Dict[str, Any]) -> str:
        json_str = json.dumps(json_data, ensure_ascii=False)
        return self.send_message(json_str)
