from __future__ import annotations

from typing import Dict, List


def generate_script(topic: str, genre: str, duration_sec: int) -> Dict:
    scene_count = 4 if duration_sec <= 90 else 6
    scenes = []
    scene_templates = [
        ("문제 제기", f"{topic}에서 가장 먼저 생기는 궁금증을 짧고 강하게 던집니다.", "큰 질문 문구, 빠른 줌 인, 높은 대비의 오프닝"),
        ("상황 설명", "시청자가 바로 떠올릴 수 있는 일상적인 사례로 배경을 보여줍니다.", "인물과 아이콘을 활용한 좌우 비교 구도"),
        ("핵심 정리", "핵심 원리를 세 단계로 나누어 간단하게 설명합니다.", "1-2-3 단계 카드와 깔끔한 모션 그래픽"),
        ("행동 제안", "지금 바로 적용할 수 있는 작은 행동을 제안합니다.", "체크리스트와 밝은 엔딩 배경"),
        ("주의점", "헷갈리기 쉬운 부분과 피해야 할 실수를 정리합니다.", "경고 아이콘과 예시 화면 비교"),
        ("마무리", "전체 내용을 한 문장으로 요약하고 다음 행동을 안내합니다.", "핵심 문장 타이포그래피와 부드러운 페이드아웃"),
    ]
    for index, (label, narration, visual) in enumerate(scene_templates[:scene_count], start=1):
        scenes.append(
            {
                "no": index,
                "narration": f"{label}: {narration}",
                "visual": visual,
            }
        )
    return {
        "title": f"{topic} 쉽게 이해하기",
        "hook": f"{topic}, 어렵게 느껴졌다면 이 순서로 보세요.",
        "scenes": scenes,
        "cta": "도움이 되었다면 저장하고 다음 제작 아이디어도 이어서 정리해 보세요.",
        "note": "API 키 없이 로컬 템플릿으로 생성된 초안입니다.",
    }


def generate_visual_prompts(scenes: List[Dict], style: str, ratio: str) -> List[Dict]:
    results = []
    for scene in scenes:
        visual = scene.get("visual") or scene.get("narration", "")
        results.append(
            {
                "no": scene.get("no", len(results) + 1),
                "prompt": (
                    f"{style} style, {ratio} composition, clear subject, readable visual metaphor, "
                    f"scene concept: {visual}, high quality, clean lighting"
                ),
                "negative": "blurry, unreadable text, distorted hands, watermark, logo",
            }
        )
    return results


def generate_metadata(title: str, topic: str, scenes: List[Dict]) -> Dict:
    base_title = title or f"{topic} 쉽게 이해하기" or "영상 제목"
    clean_topic = topic or base_title
    return {
        "titles": [
            base_title,
            f"{clean_topic} 한 번에 정리",
            f"{clean_topic} 초보자도 이해하는 핵심",
        ],
        "description": (
            f"{clean_topic}의 핵심을 장면별로 정리한 영상입니다. "
            "대본, 시각화 아이디어, 자막 초안을 함께 활용해 보세요."
        ),
        "tags": [clean_topic, "유튜브", "정보", "쇼츠", "영상제작"],
        "hashtags": ["#정보", "#유튜브", "#쇼츠"],
        "scene_count": len(scenes),
    }
