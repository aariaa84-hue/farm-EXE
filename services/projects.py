from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


PROJECT_DIR = Path("data/projects")


def _safe_slug(text: str) -> str:
    text = (text or "project").strip().lower()
    text = re.sub(r"[^0-9a-zA-Z가-힣_-]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:60] or "project"


def save_project(project: Dict[str, Any]) -> Dict[str, Any]:
    PROJECT_DIR.mkdir(parents=True, exist_ok=True)
    if not project.get("id"):
        project["id"] = str(uuid.uuid4())
    project["updated_at"] = datetime.now().isoformat(timespec="seconds")
    slug = _safe_slug(project.get("title") or project.get("topic") or project["id"])
    path = PROJECT_DIR / f"{slug}-{project['id'][:8]}.json"
    path.write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8")
    project["_path"] = str(path)
    return project


def list_projects() -> List[Dict[str, Any]]:
    PROJECT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for file in sorted(PROJECT_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            item = json.loads(file.read_text(encoding="utf-8"))
            rows.append(
                {
                    "id": item.get("id"),
                    "title": item.get("title") or item.get("topic") or file.stem,
                    "updated_at": item.get("updated_at", ""),
                    "path": str(file),
                }
            )
        except json.JSONDecodeError:
            continue
    return rows
