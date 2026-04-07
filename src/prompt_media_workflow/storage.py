from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


DATA_ROOT = Path(os.getenv("PMW_DATA_ROOT", "data"))


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(relative_path: str, payload: Any) -> Path:
    output_path = DATA_ROOT / relative_path
    ensure_parent(output_path)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return output_path


def read_json(relative_path: str) -> Any:
    input_path = DATA_ROOT / relative_path
    with input_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
