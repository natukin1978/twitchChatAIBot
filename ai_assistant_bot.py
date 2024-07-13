import asyncio
import json
import re

import aiohttp
import twitchio
from aiohttp import web
from bs4 import BeautifulSoup
from twitchio.ext import commands

from config_helper import readConfig
from genai import Genai
from text_helper import readText

BASE_PROMPT = readText("prompts/base_prompt.txt")
WEB_SCRAPING_PROMPT = readText("prompts/web_scraping_prompt.txt")
WEB_SCRAPING_MESSAGE = readText("messages/web_scraping_message.txt")

config = readConfig()

# TwitchのOAuthトークン
ACCESS_TOKEN = config["twitch"]["accessToken"]
# Twitchチャンネルの名前
CHANNEL_NAME = config["twitch"]["loginChannel"]

WEB_SCRAPING_APIKEY = config["phantomJsCloud"]["apiKey"]


def find_url(text: str) -> str:
    # 正規表現パターン
    # このパターンは、httpやhttpsプロトコルを含むURLを検索します。
    # 特に、ドメイン名やサブドメイン、ポート番号などを考慮しています。
    RE_URL = r'\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`()\[\]{};:\'".,<>?«»“”‘’]))'

    urls = re.findall(RE_URL, text)
    if not urls:
        return ""

    # 最初の要素だけを返す
    return urls[0][0]


async def web_scraping(url: str, renderType: str) -> str:
    param = {
        "url": url,
        "renderType": renderType,
    }
    API_URL = "http://PhantomJScloud.com/api/browser/v2/" + WEB_SCRAPING_APIKEY + "/"
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, data=json.dumps(param)) as response:
            return await response.text()


def get_all_contents(html_content: str, target_selector: str) -> list:
    soup = BeautifulSoup(html_content, "html.parser")
    elem = soup.select_one(target_selector)
    elem_strings = elem.stripped_strings
    return [elem_string for elem_string in elem_strings]


class Bot(commands.Bot):
    def __init__(self, genai: Genai):
        super().__init__(
            token=ACCESS_TOKEN,
            prefix="!",
            initial_channels=[CHANNEL_NAME],
        )
        self.genai = genai

    async def event_message(self, msg: twitchio.Message):
        if msg.echo:
            return

        if msg.content.startswith("!"):
            await self.handle_commands(msg)
            return

        text = msg.content
        if WEB_SCRAPING_APIKEY:
            url = find_url(text)
            if url:
                await msg.channel.send(WEB_SCRAPING_MESSAGE)

                content = None
                if "www.twitch.tv" in url:
                    content = await web_scraping(url, "html")
                    contents_list = get_all_contents(
                        content, "[class*='channel-info-content']"
                    )
                    content = "\n".join(contents_list)
                else:
                    content = await web_scraping(url, "plainText")

                response_text = self.genai.send_message_with_always_prompt(
                    WEB_SCRAPING_PROMPT + "\n" + content
                )
                await msg.channel.send(response_text)

    @commands.command(name="ai")
    async def cmd_ai(self, ctx: commands.Context):
        pattern = r"^!ai (.*?)$"
        match = re.search(pattern, ctx.message.content)
        if not match:
            print("Not match")
            return

        message = match.group(1)
        response_text = self.genai.send_message_with_always_prompt(message)
        await ctx.send(response_text)


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
            await client.get_channel(CHANNEL_NAME).send(response_text)
            return web.Response(text="Message sent to Twitch chat")
        else:
            return web.Response(status=400, text="No message found in request")

    client = twitchio.Client(
        token=ACCESS_TOKEN,
        initial_channels=[CHANNEL_NAME],
    )

    app = web.Application()
    app.router.add_get("/ai", handle)
    app.router.add_post("/ai", handle)
    runner = web.AppRunner(app)
    await runner.setup()

    conf_rs = config["recvServer"]
    site = web.TCPSite(runner, conf_rs["name"], conf_rs["port"])
    await site.start()

    genai = Genai(config)
    print("base_prompt:")
    print(BASE_PROMPT)
    print("always_prompt:")
    print(genai.ALWAYS_PROMPT)
    # 基本ルールを教える
    genai.send_message(BASE_PROMPT)

    bot = Bot(genai)
    await bot.connect()
    # await client.connect()
    await client.start()


if __name__ == "__main__":
    asyncio.run(main())
