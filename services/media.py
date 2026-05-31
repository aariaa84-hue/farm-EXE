from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, List


def seconds_to_srt_time(value: float) -> str:
    value = max(0.0, float(value))
    hours = int(value // 3600)
    minutes = int((value % 3600) // 60)
    seconds = int(value % 60)
    millis = int(round((value - math.floor(value)) * 1000))
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"


def build_srt(scenes: List[Dict], total_duration: int = 60) -> str:
    if not scenes:
        return ""
    per_scene = max(2.0, total_duration / len(scenes))
    lines = []
    for idx, scene in enumerate(scenes, start=1):
        start = (idx - 1) * per_scene
        end = idx * per_scene
        text = scene.get("narration", "").strip()
        lines.append(str(idx))
        lines.append(f"{seconds_to_srt_time(start)} --> {seconds_to_srt_time(end)}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


def export_markdown(project: Dict, path: Path) -> Path:
    scenes = project.get("scenes", [])
    metadata = project.get("metadata", {})
    prompts = project.get("visual_prompts", [])
    lines = [
        f"# {project.get('title', 'Untitled')}",
        "",
        f"- 주제: {project.get('topic', '')}",
        f"- 장르/톤: {project.get('genre', '')}",
        "",
        "## 대본",
        "",
    ]
    for scene in scenes:
        lines.append(f"### Scene {scene.get('no')}")
        lines.append(scene.get("narration", ""))
        lines.append("")
        lines.append(f"시각화: {scene.get('visual', '')}")
        lines.append("")
    if prompts:
        lines.append("## 비주얼 프롬프트")
        lines.append("")
        for p in prompts:
            lines.append(f"- Scene {p.get('no')}: {p.get('prompt')}")
    if metadata:
        lines.append("")
        lines.append("## 메타데이터")
        lines.append("")
        for title in metadata.get("titles", []):
            lines.append(f"- 제목 후보: {title}")
        lines.append("")
        lines.append(metadata.get("description", ""))
        lines.append("")
        lines.append("태그: " + ", ".join(metadata.get("tags", [])))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
