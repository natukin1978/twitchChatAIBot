import asyncio
import json
import re

import twitchio
import websockets

import global_value as g
from config_helper import readConfig
from genai import GenAI
from one_comme_users import read_one_comme_users, update_message_json
from random_helper import is_hit
from text_helper import readText
from twitch_bot import TwitchBot

g.BASE_PROMPT = readText("prompts/base_prompt.txt")
g.WEB_SCRAPING_PROMPT = readText("prompts/web_scraping_prompt.txt")
g.ERROR_MESSAGE = readText("messages/error_message.txt")
g.STOP_CANDIDATE_MESSAGE = readText("messages/stop_candidate_message.txt")
g.WEB_SCRAPING_MESSAGE = readText("messages/web_scraping_message.txt")

g.config = readConfig()

g.map_is_first_on_stream = {}
g.one_comme_users = read_one_comme_users()
g.set_exclude_id = set(readText("exclude_id.txt").splitlines())
g.talker_name = ""
g.talk_buffers = ""


async def main():
    async def connect_and_receive(uri):
        async with websockets.connect(uri) as websocket:
            while True:
                try:
                    message = await websocket.recv()
                    try:
                        data = json.loads(message)
                        # JSONとして処理する
                        g.talker_name = data["talkerName"]
                    except json.JSONDecodeError:
                        # プレーンテキストとして処理する
                        message = message.strip()
                        talk_buffers_len = len(g.talk_buffers)
                        answerLevel = 2
                        if (
                            talk_buffers_len > 1000
                            or ("教え" in message)
                            or ("調べ" in message)
                            or is_hit(answerLevel)
                        ):
                            json_data = GenAI.create_message_json()
                            json_data["id"] = g.config["twitch"]["loginChannel"]
                            json_data["displayName"] = g.talkerName
                            json_data["content"] = message.strip()
                            update_message_json(json_data)
                            response_text = genai.send_message_by_json_with_buf(
                                json_data
                            )
                            if response_text:
                                await client.get_channel(
                                    g.config["twitch"]["loginChannel"]
                                ).send(response_text)
                        else:
                            if talk_buffers_len > 0:
                                g.talk_buffers += " "
                            g.talk_buffers += message

                except websockets.exceptions.ConnectionClosed:
                    print("WebSocket connection closed")
                    break

    genai = GenAI()
    print("base_prompt:")
    print(g.BASE_PROMPT)

    client = twitchio.Client(
        token=g.config["twitch"]["accessToken"],
        initial_channels=[g.config["twitch"]["loginChannel"]],
    )
    await client.connect()

    bot = TwitchBot(genai)
    await bot.connect()

    conf_rs = g.config["recvServer"]
    websocket_uri = f"ws://{conf_rs['name']}:{conf_rs['port']}/textonly"
    websocket_task = asyncio.create_task(connect_and_receive(websocket_uri))
    await websocket_task


if __name__ == "__main__":
    asyncio.run(main())
