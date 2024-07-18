import asyncio
import re

import aiohttp
import twitchio
from aiohttp import web

import global_value as g
from config_helper import readConfig
from genai import GenAI
from text_helper import readText
from twitch_bot import TwitchBot
from talk_voice import talk_voice

g.ALWAYS_PROMPT = readText("prompts/always_prompt.txt")
g.BASE_PROMPT = readText("prompts/base_prompt.txt")
g.WEB_SCRAPING_PROMPT = readText("prompts/web_scraping_prompt.txt")
g.ERROR_MESSAGE = readText("messages/error_message.txt")
g.WEB_SCRAPING_MESSAGE = readText("messages/web_scraping_message.txt")

config = readConfig()

# TwitchのOAuthトークン
g.ACCESS_TOKEN = config["twitch"]["accessToken"]
# Twitchチャンネルの名前
g.CHANNEL_NAME = config["twitch"]["loginChannel"]

g.WEB_SCRAPING_APIKEY = config["phantomJsCloud"]["apiKey"]


async def main():
    async def handle(request):
        message = None
        if request.method == "GET":
            message = request.query["message"]
        elif request.method == "POST":
            try:
                data = await request.json()
                message = data.get("message")
            except Exception as e:
                return web.Response(status=500, text=str(e))
        else:
            return web.Response(status=405, text="Method Not Allowed")

        if message:
            response_text = genai.send_message_with_always_prompt(message)
            await talk_voice(response_text)
            await client.get_channel(g.CHANNEL_NAME).send(response_text)
            return web.Response(text="Message sent to Twitch chat")
        else:
            return web.Response(status=400, text="No message found in request")

    genai = GenAI(config)
    print("base_prompt:")
    print(g.BASE_PROMPT)
    print("always_prompt:")
    print(g.ALWAYS_PROMPT)
    # 基本ルールを教える
    response_text = genai.send_message(g.BASE_PROMPT)

    client = twitchio.Client(
        token=g.ACCESS_TOKEN,
        initial_channels=[g.CHANNEL_NAME],
    )
    await client.connect()

    app = web.Application()
    app.router.add_get("/ai", handle)
    app.router.add_post("/ai", handle)
    runner = web.AppRunner(app)
    await runner.setup()

    conf_rs = config["recvServer"]
    if conf_rs and conf_rs["name"] and conf_rs["port"]:
        site = web.TCPSite(runner, conf_rs["name"], conf_rs["port"])
        await site.start()

    bot = TwitchBot(genai)
    # await bot.connect() 終端なので下を使用する
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
