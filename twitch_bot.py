import json
import re

import aiohttp
import twitchio
from bs4 import BeautifulSoup
from twitchio.ext import commands

import global_value as g
from genai import GenAI
from talk_voice import talk_voice


class TwitchBot(commands.Bot):
    def __init__(self, genai: GenAI):
        super().__init__(
            token=g.ACCESS_TOKEN,
            prefix="!",
            initial_channels=[g.CHANNEL_NAME],
        )
        self.genai = genai

    @staticmethod
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

    @staticmethod
    async def web_scraping(url: str, renderType: str) -> str:
        param = {
            "url": url,
            "renderType": renderType,
        }
        API_URL = (
            "http://PhantomJScloud.com/api/browser/v2/" + g.WEB_SCRAPING_APIKEY + "/"
        )
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, data=json.dumps(param)) as response:
                return await response.text()

    @staticmethod
    def get_all_contents(html_content: str, target_selector: str) -> list:
        soup = BeautifulSoup(html_content, "html.parser")
        elem = soup.select_one(target_selector)
        elem_strings = elem.stripped_strings
        return [elem_string for elem_string in elem_strings]

    async def event_message(self, msg: twitchio.Message):
        if msg.echo:
            return

        if msg.content.startswith("!"):
            await self.handle_commands(msg)
            return

        text = msg.content

        json_data = GenAI.create_message_json(msg)
        json_data["content"] = text

        if g.WEB_SCRAPING_APIKEY:
            url = TwitchBot.find_url(text)
            if url:
                await talk_voice(g.WEB_SCRAPING_MESSAGE)
                await msg.channel.send(g.WEB_SCRAPING_MESSAGE)

                content = None
                if "www.twitch.tv" in url:
                    content = await TwitchBot.web_scraping(url, "html")
                    contents_list = TwitchBot.get_all_contents(
                        content, "[class*='channel-info-content']"
                    )
                    content = "\n".join(contents_list)
                else:
                    content = await TwitchBot.web_scraping(url, "plainText")

                json_data["content"] = g.WEB_SCRAPING_PROMPT + "\n" + content
                json_data["answerLength"] = 80  # Webの内容なのでちょっと大目に見る
                json_data["answerLevel"] = 2  # 常に回答してください

        response_text = self.genai.send_message_by_json(json_data)
        response_text = response_text.rstrip()
        if response_text:
            await talk_voice(response_text)
            await msg.channel.send(response_text)

    @commands.command(name="ai")
    async def cmd_ai(self, ctx: commands.Context):
        pattern = r"^!ai (.*?)$"
        match = re.search(pattern, ctx.message.content)
        if not match:
            print("Not match")
            return

        text = match.group(1)

        json_data = GenAI.create_message_json(ctx.message)
        json_data["content"] = text
        json_data["answerLevel"] = 2  # 常に回答してください
        response_text = self.genai.send_message_by_json(json_data)
        await talk_voice(response_text)
        await ctx.send(response_text)
