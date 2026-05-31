from __future__ import annotations

from .config import load_settings


def get_tts_status() -> dict:
    has_key = bool(load_settings(mask=False).get("elevenlabs_api_key", "").strip())
    if has_key:
        return {
            "enabled": True,
            "message": "ElevenLabs API 키가 저장되어 있습니다.",
        }
    return {
        "enabled": False,
        "message": "ElevenLabs API 키가 없어 TTS 기능이 비활성화되어 있습니다. 설정에서 키를 입력하면 이 안내가 사라집니다.",
    }
