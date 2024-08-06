import random
from random import randint
from typing import Any, Dict


def is_hit(percent: int) -> bool:
    if percent >= 100:
        return True
    random_value = randint(0, 100)
    return percent >= random_value


def is_hit_by_message_json(percent: int, json_data: Dict[str, Any]) -> bool:
    if json_data["isFirst"] or json_data["isFirstOnStream"]:
        # 初見さんや配信で初回の人への回答は必須
        percent = 100
    return is_hit(percent)
