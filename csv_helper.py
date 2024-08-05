import csv
from typing import Any, Dict


def readCsvToDict(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        return [row for row in reader]
