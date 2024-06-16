import asyncio
import json
import re

import google.generativeai as genai
import twitchio
from twitchio.ext import commands
from aiohttp import web

from config_helper import readConfig
from text_helper import readText

BASE_PROMPT = readText("base_prompt.txt")

config = readConfig()

# TwitchのOAuthトークン
ACCESS_TOKEN = config["twitch"]["accessToken"]
# Twitchチャンネルの名前
CHANNEL_NAME = config["twitch"]["loginChannel"]


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
            print(f"Received message: {message}")
            responseAI = genaiChat.send_message(message)
            await client.get_channel(CHANNEL_NAME).send(responseAI.text)
            return web.Response(text="Message sent to Twitch chat")
        else:
            return web.Response(status=400, text="No message found in request")

    client = twitchio.Client(
        token=ACCESS_TOKEN,
        initial_channels=[CHANNEL_NAME],
    )

    bot = commands.Bot(
        token=ACCESS_TOKEN,
        prefix="!",
        initial_channels=[CHANNEL_NAME],
    )

    @bot.command(name="ai")
    async def cmd_ai(ctx: commands.Context):
        pattern = r"^!ai (.*?)$"
        match = re.search(pattern, ctx.message.content)
        if not match:
            print("Not match")
            return

        question = match.group(1)
        responseAI = genaiChat.send_message(question)
        await ctx.send(responseAI.text)

    app = web.Application()
    app.router.add_get("/ai", handle)
    app.router.add_post("/ai", handle)
    runner = web.AppRunner(app)
    await runner.setup()

    conf_rs = config["recvServer"]
    site = web.TCPSite(runner, conf_rs["name"], conf_rs["port"])
    await site.start()

    conf_g = config["google"]
    genai.configure(api_key=conf_g["geminiApiKey"])
    genaiModel = genai.GenerativeModel(conf_g["modelName"])
    genaiChat = genaiModel.start_chat(history=[])
    # 基本ルールを教える
    print(BASE_PROMPT)
    responseAI = genaiChat.send_message(BASE_PROMPT)
    print(responseAI.text)

    await bot.connect()
    # await client.connect()
    await client.start()


if __name__ == "__main__":
    asyncio.run(main())
