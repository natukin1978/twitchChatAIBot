import datetime
import json
import os
import pickle
from typing import Any, Dict

import google.generativeai as genai
import twitchio
from google.generativeai.types import (
    HarmBlockThreshold,
    HarmCategory,
    StopCandidateException,
)

import global_value as g
from cache_helper import get_cache_filepath
from one_comme_users import update_message_json
from text_helper import readText


class GenAI:
    FILENAME_CHAT_HISTORY = get_cache_filepath(
        "twitchChatAIBot_gen_ai_chat_history.pkl"
    )

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

    def __init__(self):
        conf_g = g.config["google"]
        genai.configure(api_key=conf_g["geminiApiKey"])
        self.genaiModel = genai.GenerativeModel(
            model_name=conf_g["modelName"],
            safety_settings=self.GENAI_SAFETY_SETTINGS,
            system_instruction=g.BASE_PROMPT,
        )
        self.genaiChat = None

    @staticmethod
    def create_message_json(msg: twitchio.Message = None) -> Dict[str, Any]:
        localtime = datetime.datetime.now()
        localtime_iso_8601 = localtime.isoformat()
        json_data = {
            "dateTime": localtime_iso_8601,
            "id": None,
            "displayName": None,
            "nickname": None,
            "content": None,  # 関数外で設定してね
            "isFirst": False,
            "isFirstOnStream": None,  # すぐ下で設定する
            "answerLength": 35,
        }
        if msg:
            json_data["id"] = msg.author.name
            json_data["displayName"] = msg.author.display_name
            json_data["isFirst"] = msg.first
        update_message_json(json_data)
        return json_data

    def get_chat(self):
        if not self.genaiChat:
            self.genaiChat = self.genaiModel.start_chat(history=[])
        return self.genaiChat

    def load_chat_history(self) -> bool:
        if not os.path.isfile(self.FILENAME_CHAT_HISTORY):
            return False
        with open(self.FILENAME_CHAT_HISTORY, "rb") as f:
            chat_history = pickle.load(f)
            self.genaiChat = self.genaiModel.start_chat(history=chat_history)
            return True

    def save_chat_history(self) -> None:
        with open(self.FILENAME_CHAT_HISTORY, "wb") as f:
            pickle.dump(self.get_chat().history, f)

    def send_message(self, message: str) -> str:
        try:
            print(message)
            response = self.get_chat().send_message(message)
            response_text = response.text.rstrip()
            print(response_text)
            self.save_chat_history()
            return response_text
        except StopCandidateException as e:
            print(e)
            return g.STOP_CANDIDATE_MESSAGE
        except IndexError as e:
            print(e)
            return ""
        except Exception as e:
            print(e)
            return g.ERROR_MESSAGE

    def send_message_by_json(self, json_data: Dict[str, Any]) -> str:
        json_str = json.dumps(json_data, ensure_ascii=False)
        return self.send_message(json_str)

    def send_message_by_json_with_buf(self, json_data: Dict[str, Any]) -> str:
        if len(g.talk_buffers) > 0:
            # 溜まってたバッファ分を送ってクリアする
            json_data_buffer = GenAI.create_message_json()
            json_data_buffer["id"] = g.config["twitch"]["loginChannel"]
            json_data_buffer["displayName"] = g.talker_name
            json_data_buffer["content"] = g.talk_buffers
            update_message_json(json_data_buffer)
            g.talk_buffers = ""
            self.send_message_by_json(json_data_buffer)
        # 本命
        return self.send_message_by_json(json_data)
