import os


def readText(name: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, name)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
