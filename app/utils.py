import json
import os
from pathlib import Path


def ensure_dir(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def dumps_json(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def loads_json(value: str):
    try:
        return json.loads(value) if value else None
    except Exception:
        return None
