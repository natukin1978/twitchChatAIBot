import asyncio
import json
import re

import google.generativeai as genai
import twitchio
from twitchio.ext import commands
from aiohttp import web

from config_helper import readConfig
from text_helper import readText

BASE_PROMPT = readText("prompts/base_prompt.txt")
ALWAYS_PROMPT = readText("prompts/always_prompt.txt")
ERROR_MESSAGE = readText("messages/error_message.txt")

config = readConfig()

# TwitchのOAuthトークン
ACCESS_TOKEN = config["twitch"]["accessToken"]
# Twitchチャンネルの名前
CHANNEL_NAME = config["twitch"]["loginChannel"]


async def main():
    def send_message_with_always_prompt(
        genaiChat: genai.ChatSession, message: str
    ) -> genai.protos.GenerateContentResponse:
        try:
            print(message)
            return genaiChat.send_message(message + "\n" + ALWAYS_PROMPT)
        except Exception as e:
            print(e)
            return {"text": ERROR_MESSAGE}

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
            responseAI = send_message_with_always_prompt(genaiChat, message)
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

        message = match.group(1)
        responseAI = send_message_with_always_prompt(genaiChat, message)
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
    print("base_prompt:")
    print(BASE_PROMPT)
    print("always_prompt:")
    print(ALWAYS_PROMPT)
    # 基本ルールを教える
    responseAI = genaiChat.send_message(BASE_PROMPT)
    print(responseAI.text)

    await bot.connect()
    # await client.connect()
    await client.start()


if __name__ == "__main__":
    asyncio.run(main())
