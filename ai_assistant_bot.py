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
from talk_voice import talk_voice, set_voice_effect
from one_comme_users import update_message_json, read_one_comme_users

g.BASE_PROMPT = readText("prompts/base_prompt.txt")
g.WEB_SCRAPING_PROMPT = readText("prompts/web_scraping_prompt.txt")
g.ERROR_MESSAGE = readText("messages/error_message.txt")
g.STOP_CANDIDATE_MESSAGE = readText("messages/stop_candidate_message.txt")
g.WEB_SCRAPING_MESSAGE = readText("messages/web_scraping_message.txt")

g.config = readConfig()

g.map_is_first_on_stream = {}
g.one_comme_users = read_one_comme_users()


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
            json_data = GenAI.create_message_json()
            json_data["id"] = g.config["twitch"]["loginChannel"]
            json_data["content"] = message
            json_data["answerLevel"] = 100  # 常に回答してください
            update_message_json(json_data)
            response_text = genai.send_message_by_json(json_data)
            if response_text:
                await talk_voice(response_text)
                await client.get_channel(g.config["twitch"]["loginChannel"]).send(
                    response_text
                )
            return web.Response(text="Message sent to Twitch chat")
        else:
            return web.Response(status=400, text="No message found in request")

    configAS = g.config["assistantSeika"]
    await set_voice_effect("speed", configAS["speed"])
    await set_voice_effect("volume", configAS["volume"])

    genai = GenAI()
    print("base_prompt:")
    print(g.BASE_PROMPT)

    client = twitchio.Client(
        token=g.config["twitch"]["accessToken"],
        initial_channels=[g.config["twitch"]["loginChannel"]],
    )
    await client.connect()

    app = web.Application()
    app.router.add_get("/ai", handle)
    app.router.add_post("/ai", handle)
    runner = web.AppRunner(app)
    await runner.setup()

    conf_rs = g.config["recvServer"]
    if conf_rs and conf_rs["name"] and conf_rs["port"]:
        site = web.TCPSite(runner, conf_rs["name"], conf_rs["port"])
        await site.start()

    bot = TwitchBot(genai)
    # await bot.connect() 終端なので下を使用する
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
