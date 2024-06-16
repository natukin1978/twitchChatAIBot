import asyncio
import json

import google.generativeai as genai
import twitchio
from aiohttp import web

from config_helper import readConfig

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
            responseAI = genaiModel.generate_content(
                message + "\n" + config["basePrompt"]
            )
            await client.get_channel(CHANNEL_NAME).send(responseAI.text)
            return web.Response(text="Message sent to Twitch chat")
        else:
            return web.Response(status=400, text="No message found in request")

    client = twitchio.Client(
        token=ACCESS_TOKEN,
        initial_channels=[CHANNEL_NAME],
    )

    genai.configure(api_key=config["google"]["geminiApiKey"])
    genaiModel = genai.GenerativeModel(config["google"]["modelName"])

    app = web.Application()
    app.router.add_get("/ai", handle)
    app.router.add_post("/ai", handle)
    runner = web.AppRunner(app)
    await runner.setup()

    conf_rs = config["recvServer"]
    site = web.TCPSite(runner, conf_rs["name"], conf_rs["port"])
    await site.start()

    await client.start()


if __name__ == "__main__":
    asyncio.run(main())
