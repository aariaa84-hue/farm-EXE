from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


APP_DIR = Path(
    os.getenv("CLEANTUBE_HOME")
    or (Path(os.getenv("LOCALAPPDATA")) / "CleanTubeStudio" if os.getenv("LOCALAPPDATA") else Path.home() / ".cleantube_studio")
)
FALLBACK_APP_DIR = Path("data/settings")


DEFAULTS: Dict[str, Any] = {
    "elevenlabs_api_key": "",
    "download_dir": str(Path.home() / "Downloads"),
}


def _config_file() -> Path:
    try:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        return APP_DIR / "settings.json"
    except OSError:
        FALLBACK_APP_DIR.mkdir(parents=True, exist_ok=True)
        return FALLBACK_APP_DIR / "settings.json"


def load_settings(mask: bool = False) -> Dict[str, Any]:
    config_file = _config_file()
    data = DEFAULTS.copy()
    if config_file.exists():
        try:
            saved = json.loads(config_file.read_text(encoding="utf-8"))
            data.update({key: saved.get(key, value) for key, value in DEFAULTS.items()})
        except json.JSONDecodeError:
            pass
    if mask and data.get("elevenlabs_api_key"):
        data["elevenlabs_api_key"] = mask_secret(data["elevenlabs_api_key"])
    return data


def save_settings(payload: Dict[str, Any]) -> Dict[str, Any]:
    config_file = _config_file()
    current = load_settings(mask=False)
    for key in DEFAULTS:
        if key in payload:
            value = payload[key]
            if key == "elevenlabs_api_key" and isinstance(value, str) and value.startswith("••••"):
                continue
            current[key] = value
    config_file.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
    return current


def mask_secret(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 10:
        return "••••"
    return f"{value[:4]}••••{value[-4:]}"
