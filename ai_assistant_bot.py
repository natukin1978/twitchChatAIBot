import asyncio
import json
import os
import pickle
import socket
import sys

import twitchio
import websockets

import global_value as g
from cache_helper import get_cache_filepath
from config_helper import readConfig
from genai_chat import GenAIChat
from one_comme_users import (
    load_is_first_on_stream,
    read_one_comme_users,
    update_message_json,
)
from random_helper import is_hit
from text_helper import readText
from twitch_bot import TwitchBot
from youtube_bot import YoutubeBot

g.BASE_PROMPT = readText("prompts/base_prompt.txt")
g.WEB_SCRAPING_PROMPT = readText("prompts/web_scraping_prompt.txt")
g.ADDITIONAL_REQUESTS_PROMPT = readText("prompts/additional_requests_prompt.txt")
g.ERROR_MESSAGE = readText("messages/error_message.txt")
g.STOP_CANDIDATE_MESSAGE = readText("messages/stop_candidate_message.txt")
g.WEB_SCRAPING_MESSAGE = readText("messages/web_scraping_message.txt")

g.config = readConfig()

g.map_is_first_on_stream = {}
g.one_comme_users = read_one_comme_users()
g.set_exclude_id = set(readText("exclude_id.txt").splitlines())
g.talker_name = ""
g.talk_buffers = ""
g.live_video_id = ""

FILENAME_LIVE_VIDEO_ID = get_cache_filepath("twitchChatAIBot_live_video_id.pkl")


def load_live_video_id() -> bool:
    if not os.path.isfile(FILENAME_LIVE_VIDEO_ID):
        return False
    with open(FILENAME_LIVE_VIDEO_ID, "rb") as f:
        g.live_video_id = pickle.load(f)
        return True


def save_live_video_id() -> None:
    with open(FILENAME_LIVE_VIDEO_ID, "wb") as f:
        pickle.dump(g.live_video_id, f)


async def main():
    def has_response_keywords(message: str) -> bool:
        conf_nia = g.config["neoInnerApi"]
        response_keywords = conf_nia["responseKeywords"]
        return next(filter(lambda v: v in message, response_keywords), None)

    def has_exclusion_keywords(message: str) -> bool:
        conf_nia = g.config["neoInnerApi"]
        exclusion_keywords = conf_nia["exclusionKeywords"]
        return next(filter(lambda v: v in message, exclusion_keywords), None)

    async def recv_message(message: str) -> None:
        try:
            data = json.loads(message)
            if type(data) is not dict:
                raise json.JSONDecodeError("result value was not dict", "", "")
            # JSONとして処理する
            g.talker_name = data["talkerName"]
        except json.JSONDecodeError:
            # プレーンテキストとして処理する
            message = message.strip()
            if len(message) <= 1 or has_exclusion_keywords(message):
                # 1文字や除外キーワードは取り込まない
                return

            is_response = has_response_keywords(message)
            talk_buffers_len = len(g.talk_buffers)
            answerLevel = 2
            if is_response or talk_buffers_len > 1000 or is_hit(answerLevel):
                json_data = GenAIChat.create_message_json()
                json_data["id"] = g.config["twitch"]["loginChannel"]
                json_data["displayName"] = g.talker_name
                json_data["content"] = message.strip()
                update_message_json(json_data)
                if is_response:
                    # レスポンス有効時は追加の要望を無効化
                    del json_data["additionalRequests"]
                response_text = genai_chat.send_message_by_json_with_buf(json_data)
                if response_text:
                    await client.get_channel(g.config["twitch"]["loginChannel"]).send(
                        response_text
                    )
            else:
                if talk_buffers_len > 0:
                    g.talk_buffers += " "
                g.talk_buffers += message

    async def websocket_listen_forever(websocket_uri: str) -> None:
        reply_timeout = 60
        ping_timeout = 15
        sleep_time = 5
        while True:
            # outer loop restarted every time the connection fails
            try:
                async with websockets.connect(websocket_uri) as ws:
                    while True:
                        # listener loop
                        try:
                            message = await asyncio.wait_for(
                                ws.recv(), timeout=reply_timeout
                            )
                            await recv_message(message)
                        except (
                            asyncio.TimeoutError,
                            websockets.exceptions.ConnectionClosed,
                        ):
                            try:
                                pong = await ws.ping()
                                await asyncio.wait_for(pong, timeout=ping_timeout)
                                continue
                            except:
                                await asyncio.sleep(sleep_time)
                                break
            except Exception as e:
                print(e, file=sys.stderr)
                await asyncio.sleep(sleep_time)
                continue

    async def run_forever():
        while True:
            await asyncio.sleep(15)

    print("前回の続きですか？(y/n)")
    is_continue = input() == "y"
    if is_continue and load_is_first_on_stream() and load_live_video_id():
        print("挨拶キャッシュを復元しました。")

    genai_chat = GenAIChat()

    if is_continue:
        print("会話履歴を復元しますか？(y/n)")
        is_load_chat_history = input() == "y"
        if is_load_chat_history and genai_chat.load_chat_history():
            print("会話履歴を復元しました。")

    client = twitchio.Client(
        token=g.config["twitch"]["accessToken"],
        initial_channels=[g.config["twitch"]["loginChannel"]],
    )
    await client.connect()

    bot = TwitchBot(genai_chat)
    await bot.connect()

    if not g.live_video_id:
        print("live video id:")
        g.live_video_id = input()
    if g.live_video_id:
        bot2 = YoutubeBot(genai_chat, client)
        await bot2.run()
        save_live_video_id()

    print("base_prompt:")
    print(g.BASE_PROMPT)

    conf_nia = g.config["neoInnerApi"]
    if conf_nia and conf_nia["name"] and conf_nia["port"]:
        websocket_uri = f"ws://{conf_nia['name']}:{conf_nia['port']}/textonly"
        websocket_task = asyncio.create_task(websocket_listen_forever(websocket_uri))
    else:
        # ダミーのタスク
        websocket_task = asyncio.create_task(run_forever())
    await websocket_task


if __name__ == "__main__":
    asyncio.run(main())
