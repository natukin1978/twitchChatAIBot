import asyncio
import datetime

from googleapiclient.discovery import build

import global_value as g
from genai_chat import GenAIChat
from one_comme_users import update_message_json
from random_helper import is_hit_by_message_json


class YoutubeBot:
    def __init__(self, genai_chat: GenAIChat, twitchio_client):
        self.genai_chat = genai_chat
        self.twitchio_client = twitchio_client
        self.api_key = g.config["youtube"]["apiKey"]
        self.chat_polling_interval = g.config["youtube"]["chatPollingIntervalSec"]
        self.youtube = build("youtube", "v3", developerKey=self.api_key)
        self.chat_task = None
        self.live_chat_id = None

    @staticmethod
    def create_message_json(item=None) -> dict[str, any]:
        localtime = datetime.datetime.now()
        localtime_iso_8601 = localtime.isoformat()
        json_data = {
            "dateTime": localtime_iso_8601,
            "id": None,
            "displayName": None,
            "nickname": None,
            "content": None,
            "isFirst": False,
            "isFirstOnStream": None,  # すぐ下で設定する
            "additionalRequests": None,
        }
        if item:
            snippet = item["snippet"]
            author = item["authorDetails"]
            json_data["displayName"] = author["displayName"]
            json_data["content"] = snippet["displayMessage"]
        update_message_json(json_data)
        return json_data

    async def on_message(self, items):
        for item in items:
            snippet = item["snippet"]
            author = item["authorDetails"]
            answerLevel = 16  # 1/6くらいの確率
            json_data = YoutubeBot.create_message_json(item)
            response_text = self.genai_chat.send_message_by_json_with_buf(json_data)
            if response_text and is_hit_by_message_json(answerLevel, json_data):
                await self.twitchio_client.get_channel(
                    g.config["twitch"]["loginChannel"]
                ).send(response_text)

    async def get_live_chat_id(self):
        try:
            videos_request = self.youtube.videos().list(
                part="liveStreamingDetails", id=g.live_video_id
            )
            videos_response = videos_request.execute()

            vr_items = videos_response["items"]
            if not vr_items:
                print("Invalid video ID or not a live stream.")
                return None

            self.live_chat_id = vr_items[0]["liveStreamingDetails"]["activeLiveChatId"]
            return self.live_chat_id
        except Exception as e:
            print(f"Error getting live chat ID: {e}")
            return None

    async def get_chat_messages(self):
        if not self.live_chat_id:
            print("Live chat ID is not set. Please call get_live_chat_id first.")
            return

        next_page_token = None
        try:
            while True:
                param = {
                    "part": "id,snippet,authorDetails",
                    "liveChatId": self.live_chat_id,
                    "key": self.api_key,
                }
                if next_page_token:
                    param["pageToken"] = next_page_token

                request = self.youtube.liveChatMessages().list(**param)
                response = request.execute()
                items = response.get("items", [])
                await self.on_message(items)
                next_page_token = response.get("nextPageToken")
                await asyncio.sleep(self.chat_polling_interval)
        except asyncio.CancelledError:
            print("Chat message task cancelled.")
        except Exception as e:
            print(f"Chat message get error:{e}")

    async def run(self):
        self.live_chat_id = await self.get_live_chat_id()
        if not self.live_chat_id:
            return
        self.chat_task = asyncio.create_task(self.get_chat_messages())
        # try:
        #    while True:
        #        await asyncio.sleep(10)
        # except asyncio.CancelledError:
        #    print("Main task cancelled.")
        # except KeyboardInterrupt:
        #    print("Keyboard interrupt received.")
        # finally:
        #    if self.chat_task and not self.chat_task.done():
        #        self.chat_task.cancel()
        #        await self.chat_task # キャンセルが完了するまで待機
