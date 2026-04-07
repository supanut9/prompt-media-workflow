from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "internal.json"
ENV_PATH = ROOT / ".env"


def load_dotenv(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def load_internal_config() -> dict:
    load_dotenv()
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def get_openai_api_key() -> str | None:
    load_dotenv()
    return os.getenv("OPENAI_API_KEY")
