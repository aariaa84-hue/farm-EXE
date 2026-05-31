from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


APP_DIR = Path(os.getenv("CLEANTUBE_HOME", Path.home() / ".cleantube_studio"))
CONFIG_FILE = APP_DIR / "settings.json"


DEFAULTS: Dict[str, Any] = {
    "api_base_url": "https://api.openai.com/v1",
    "api_key": "",
    "model": "gpt-4o-mini",
    "download_dir": str(Path.home() / "Downloads"),
}


def _ensure_dir() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)


def load_settings(mask: bool = False) -> Dict[str, Any]:
    _ensure_dir()
    data = DEFAULTS.copy()
    if CONFIG_FILE.exists():
        try:
            data.update(json.loads(CONFIG_FILE.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            pass
    if mask and data.get("api_key"):
        data["api_key"] = mask_secret(data["api_key"])
    return data


def save_settings(payload: Dict[str, Any]) -> Dict[str, Any]:
    _ensure_dir()
    current = load_settings(mask=False)
    for key in DEFAULTS:
        if key in payload:
            value = payload[key]
            if key == "api_key" and isinstance(value, str) and value.startswith("••••"):
                continue
            current[key] = value
    CONFIG_FILE.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
    return current


def mask_secret(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 10:
        return "••••"
    return f"{value[:4]}••••{value[-4:]}"
