from __future__ import annotations

from pathlib import Path
from typing import Dict
import os
import sys
import threading
import webbrowser

from flask import Flask, jsonify, render_template, request, send_file

from services.ai import generate_metadata, generate_script, generate_visual_prompts
from services.config import load_settings, save_settings
from services.media import build_srt, export_markdown
from services.projects import list_projects, save_project


def resource_path(relative: str) -> str:
    """Return a path that works both in source mode and PyInstaller one-file mode."""
    base = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
    return str(Path(base) / relative)


app = Flask(
    __name__,
    template_folder=resource_path("templates"),
    static_folder=resource_path("static"),
)
app.config["JSON_AS_ASCII"] = False


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/settings")
def api_settings_get():
    return jsonify(load_settings(mask=True))


@app.post("/api/settings")
def api_settings_post():
    payload = request.get_json(force=True, silent=True) or {}
    save_settings(payload)
    return jsonify({"ok": True, "settings": load_settings(mask=True)})


@app.get("/api/projects")
def api_projects():
    return jsonify({"projects": list_projects()})


@app.post("/api/script")
def api_script():
    payload: Dict = request.get_json(force=True, silent=True) or {}
    topic = payload.get("topic", "").strip()
    if not topic:
        return jsonify({"error": "topic is required"}), 400
    genre = payload.get("genre", "정보형")
    duration = int(payload.get("duration_sec") or 60)
    script = generate_script(topic=topic, genre=genre, duration_sec=duration)
    return jsonify(script)


@app.post("/api/prompts")
def api_prompts():
    payload: Dict = request.get_json(force=True, silent=True) or {}
    scenes = payload.get("scenes", [])
    style = payload.get("style", "clean Korean explainer animation")
    ratio = payload.get("ratio", "9:16")
    prompts = generate_visual_prompts(scenes=scenes, style=style, ratio=ratio)
    return jsonify({"visual_prompts": prompts})


@app.post("/api/metadata")
def api_metadata():
    payload: Dict = request.get_json(force=True, silent=True) or {}
    metadata = generate_metadata(
        title=payload.get("title", "영상 제목"),
        topic=payload.get("topic", ""),
        scenes=payload.get("scenes", []),
    )
    return jsonify(metadata)


@app.post("/api/save")
def api_save():
    payload: Dict = request.get_json(force=True, silent=True) or {}
    project = save_project(payload)
    return jsonify({"ok": True, "project": project})


@app.post("/api/export/markdown")
def api_export_markdown():
    payload: Dict = request.get_json(force=True, silent=True) or {}
    project = save_project(payload)
    title = project.get("title") or project.get("topic") or "project"
    safe = "".join(ch if ch.isalnum() or ch in "-_가-힣" else "_" for ch in title)[:50]
    path = Path("exports") / f"{safe}-{project['id'][:8]}.md"
    export_markdown(project, path)
    return jsonify({"ok": True, "path": str(path)})


@app.post("/api/export/srt")
def api_export_srt():
    payload: Dict = request.get_json(force=True, silent=True) or {}
    srt = build_srt(payload.get("scenes", []), int(payload.get("duration_sec") or 60))
    path = Path("exports") / "subtitles.srt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(srt, encoding="utf-8")
    return send_file(path, as_attachment=True, download_name="subtitles.srt")


def open_browser_once() -> None:
    webbrowser.open("http://127.0.0.1:5055")


if __name__ == "__main__":
    # debug=False avoids the auto-reloader opening two browser windows.
    threading.Timer(1.0, open_browser_once).start()
    app.run(host="127.0.0.1", port=5055, debug=False)
