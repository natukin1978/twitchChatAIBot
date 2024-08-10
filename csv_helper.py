import csv
import os
from typing import Any, List


def read_csv_to_list(path: str) -> List[List[Any]]:
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        return [row for row in reader]
