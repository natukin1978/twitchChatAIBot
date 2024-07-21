import aiohttp


async def talk_voice(text: str) -> None:
    try:
        url = "http://localhost:7180/PLAYASYNC2/90011/" + text
        auth = aiohttp.BasicAuth(
            login="SeikaServerUser", password="SeikaServerPassword"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url, auth=auth) as response:
                print(await response.text())
    except Exception as e:
        pass
