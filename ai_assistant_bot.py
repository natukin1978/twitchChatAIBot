import asyncio
import re

import twitchio
import websockets

import global_value as g
from config_helper import readConfig
from genai import GenAI
from text_helper import readText
from twitch_bot import TwitchBot
from one_comme_users import update_message_json, read_one_comme_users

g.BASE_PROMPT = readText("prompts/base_prompt.txt")
g.WEB_SCRAPING_PROMPT = readText("prompts/web_scraping_prompt.txt")
g.ERROR_MESSAGE = readText("messages/error_message.txt")
g.STOP_CANDIDATE_MESSAGE = readText("messages/stop_candidate_message.txt")
g.WEB_SCRAPING_MESSAGE = readText("messages/web_scraping_message.txt")

g.config = readConfig()

g.map_is_first_on_stream = {}
g.one_comme_users = read_one_comme_users()
g.set_exclude_id = set(readText("exclude_id.txt").splitlines())


async def main():
    async def connect_and_receive(uri):
        async with websockets.connect(uri) as websocket:
            while True:
                try:
                    response = await websocket.recv()
                    print(f"Received from WebSocket: {response}")
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

    # WebSocket の設定
    websocket_uri = "ws://127.0.0.1:50000/textonly"
    websocket_task = asyncio.create_task(connect_and_receive(websocket_uri))
    await websocket_task

if __name__ == "__main__":
    asyncio.run(main())
