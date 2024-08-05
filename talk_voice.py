import aiohttp

from typing import Any
import global_value as g


async def _request_voice_base(suffix_param: str) -> aiohttp.ClientResponse:
    configAS = g.config["assistantSeika"]
    url = f"http://{configAS['name']}:{configAS['port']}/{suffix_param}"
    auth = aiohttp.BasicAuth(login=configAS["login"], password=configAS["password"])
    async with aiohttp.ClientSession() as session:
        async with session.get(url, auth=auth) as response:
            return response


async def set_voice_effect(param: str, value: Any) -> None:
    try:
        configAS = g.config["assistantSeika"]
        cid = configAS["cid"]
        if not cid:
            return
        suffix_param = f"EFFECT/{cid}/{param}/{value}"
        await _request_voice_base(suffix_param)
    except Exception as e:
        print(e)


async def talk_voice(text: str) -> None:
    try:
        configAS = g.config["assistantSeika"]
        cid = configAS["cid"]
        if not cid:
            return
        suffix_param = f"PLAYASYNC2/{cid}/{text}"
        await _request_voice_base(suffix_param)
    except Exception as e:
        print(e)
