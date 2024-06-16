import re
import sys
from typing import Optional

import google.generativeai as genai
from twitchio import Channel, Message
from twitchio.ext import commands, eventsub

from config_helper import readConfig

config = readConfig()


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=config["twitch"]["accessToken"],
            prefix="!",
            initial_channels=[config["twitch"]["loginChannel"]],
        )
        genai.configure(api_key=config["google"]["geminiApiKey"])
        self.genaiModel = genai.GenerativeModel(config["google"]["modelName"])

    async def event_channel_joined(self, channel: Channel):
        print(f"ログインしました。チャンネル名: {channel.name}")
        for chatter in channel.chatters:
            print(f"ユーザーID: {chatter.id}")
            print(f"ユーザー名: {chatter.name}")
            print(f"表示名: {chatter.display_name}")

    async def event_ready(self):
        print("全てのチャンネルにログインしました。")
        print(f"ユーザーID: {self.user_id}")
        print(f"ユーザー名: {self.nick}")

    # !ai
    @commands.command(name="ai")
    async def cmd_ai(self, ctx: commands.Context):
        pattern = r"^!ai (.*?)$"
        match = re.search(pattern, ctx.message.content)
        if not match:
            print("マッチなし")
            return

        question = match.group(1)
        response = self.genaiModel.generate_content(
            question + "\n" + config["basePrompt"]
        )
        await ctx.send(response.text)


def main():
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
