from __future__ import annotations

import json
import re
from typing import Dict, List

import requests

from .config import load_settings


SYSTEM_PROMPT = (
    "You are a Korean YouTube production assistant. "
    "Return practical, structured Korean output. Avoid copyrighted source imitation."
)


def _call_chat(prompt: str, temperature: float = 0.7) -> str | None:
    settings = load_settings(mask=False)
    api_key = settings.get("api_key", "")
    base_url = str(settings.get("api_base_url", "")).rstrip("/")
    model = settings.get("model", "gpt-4o-mini")
    if not api_key or not base_url:
        return None

    url = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def generate_script(topic: str, genre: str, duration_sec: int) -> Dict:
    prompt = f"""
다음 주제로 유튜브 쇼츠/롱폼 영상 대본을 작성해 주세요.

주제: {topic}
장르/톤: {genre}
목표 길이: 약 {duration_sec}초

JSON으로만 반환:
{{
  "title": "...",
  "hook": "...",
  "scenes": [
    {{"no": 1, "narration": "...", "visual": "..."}}
  ],
  "cta": "..."
}}
""".strip()
    raw = _call_chat(prompt)
    parsed = _try_json(raw) if raw else None
    if parsed:
        return parsed

    scenes = [
        {
            "no": 1,
            "narration": f"{topic}에 대해 가장 먼저 알아야 할 핵심 질문을 던집니다.",
            "visual": "강한 대비의 오프닝 화면, 큰 질문 문구, 빠른 줌 인",
        },
        {
            "no": 2,
            "narration": "문제 상황을 짧고 구체적인 사례로 보여줍니다.",
            "visual": "상황을 상징하는 인물과 아이콘, 좌우 비교 구도",
        },
        {
            "no": 3,
            "narration": "핵심 원리를 세 단계로 정리합니다.",
            "visual": "1-2-3 단계 카드, 간단한 모션 그래픽",
        },
        {
            "no": 4,
            "narration": "시청자가 바로 적용할 수 있는 행동을 제안합니다.",
            "visual": "체크리스트와 밝은 엔딩 배경",
        },
    ]
    return {
        "title": f"{topic} 쉽게 이해하기",
        "hook": f"{topic}, 어렵게 느껴졌다면 이 순서로 보세요.",
        "scenes": scenes,
        "cta": "도움이 되었다면 저장하고 다음 영상도 확인해 주세요.",
    }


def generate_visual_prompts(scenes: List[Dict], style: str, ratio: str) -> List[Dict]:
    results = []
    for scene in scenes:
        visual = scene.get("visual") or scene.get("narration", "")
        results.append({
            "no": scene.get("no", len(results) + 1),
            "prompt": (
                f"{style} style, {ratio} composition, clear subject, readable visual metaphor, "
                f"scene concept: {visual}, high quality, clean lighting"
            ),
            "negative": "blurry, unreadable text, distorted hands, watermark, logo",
        })
    return results


def generate_metadata(title: str, topic: str, scenes: List[Dict]) -> Dict:
    prompt = f"""
유튜브 영상 메타데이터를 JSON으로 작성하세요.
제목 초안: {title}
주제: {topic}
장면 수: {len(scenes)}

반환 형식:
{{"titles":["..."], "description":"...", "tags":["..."], "hashtags":["..."]}}
""".strip()
    raw = _call_chat(prompt, temperature=0.5)
    parsed = _try_json(raw) if raw else None
    if parsed:
        return parsed

    return {
        "titles": [
            title,
            f"{topic} 한 번에 정리",
            f"{topic} 초보자도 이해하는 핵심",
        ],
        "description": f"{topic}의 핵심을 짧게 정리한 영상입니다. 주요 포인트를 장면별로 확인해 보세요.",
        "tags": [topic, "유튜브", "정보", "쇼츠", "영상제작"],
        "hashtags": ["#정보", "#유튜브", "#쇼츠"],
    }


def _try_json(text: str | None) -> Dict | None:
    if not text:
        return None
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.S)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
    return None
