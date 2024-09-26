import pickle
from typing import Any, Dict

import global_value as g
from cache_helper import get_cache_filepath
from csv_helper import read_csv_to_list

FILENAME_MAP_IS_FIRST_ON_STREAM = get_cache_filepath(
    "twitchChatAIBot_map_is_first_on_stream.pkl"
)


def read_one_comme_users():
    pathUsersCsv = g.config["oneComme"]["pathUsersCsv"]
    if not pathUsersCsv:
        return None

    return read_csv_to_list(pathUsersCsv)


def get_nickname(displayName: str) -> str:
    if not g.one_comme_users:
        return None

    filtered_rows = list(filter(lambda row: row[1] == displayName, g.one_comme_users))
    for filtered_row in filtered_rows:
        return filtered_row[4]

    return None


def update_nickname(json_data: Dict[str, Any]) -> None:
    nickname = get_nickname(json_data["displayName"])
    if nickname:
        json_data["nickname"] = nickname


def load_is_first_on_stream() -> None:
    with open(FILENAME_MAP_IS_FIRST_ON_STREAM, "rb") as f:
        g.map_is_first_on_stream = pickle.load(f)


def save_is_first_on_stream() -> None:
    with open(FILENAME_MAP_IS_FIRST_ON_STREAM, "wb") as f:
        pickle.dump(g.map_is_first_on_stream, f)


def update_is_first_on_stream(json_data: Dict[str, Any]) -> None:
    name = json_data["id"]
    val = None
    if name not in g.map_is_first_on_stream:
        val = True
    else:
        val = g.map_is_first_on_stream[name]
    json_data["isFirstOnStream"] = val
    g.map_is_first_on_stream[name] = False
    save_is_first_on_stream()


def update_message_json(json_data: Dict[str, Any]) -> None:
    update_is_first_on_stream(json_data)
    update_nickname(json_data)
