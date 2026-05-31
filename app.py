from __future__ import annotations

import os
import socket
import sys
import threading
import uuid
import webbrowser
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from services.video_maker import VideoBuildError, build_video


RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
APP_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
EXPORTS_DIR = APP_DIR / "exports"
UPLOADS_DIR = APP_DIR / "work" / "uploads"
EXPORTS_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(
    __name__,
    template_folder=str(RESOURCE_DIR / "templates"),
    static_folder=str(RESOURCE_DIR / "static"),
)
app.config["MAX_CONTENT_LENGTH"] = 80 * 1024 * 1024

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
DEFAULT_PORT = 5055


def _truthy(value: str | None) -> bool:
    return value in {"1", "true", "on", "yes"}


def _save_images(files) -> list[Path]:
    saved: list[Path] = []
    batch_dir = UPLOADS_DIR / uuid.uuid4().hex
    batch_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        if not file or not file.filename:
            continue
        original_name = secure_filename(file.filename)
        suffix = Path(original_name).suffix.lower()
        if suffix not in ALLOWED_IMAGE_EXTENSIONS:
            continue
        destination = batch_dir / f"{uuid.uuid4().hex}{suffix}"
        file.save(destination)
        saved.append(destination)

    return saved


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/create-video")
def create_video():
    script = request.form.get("script", "").strip()
    if not script:
        return jsonify({"ok": False, "message": "최종 대본을 입력해주세요."}), 400

    try:
        wrap_chars = max(10, min(80, int(request.form.get("wrap_chars", "24"))))
    except ValueError:
        wrap_chars = 24

    ratio = request.form.get("ratio", "16:9")
    if ratio not in {"16:9", "9:16"}:
        ratio = "16:9"

    elevenlabs_key = request.form.get("elevenlabs_key", "").strip()
    voice_id = request.form.get("voice_id", "").strip() or "21m00Tcm4TlvDq8ikWAM"
    include_subtitles = _truthy(request.form.get("include_subtitles"))
    image_paths = _save_images(request.files.getlist("images"))

    output_name = f"cleantube_{uuid.uuid4().hex[:10]}.mp4"
    output_path = EXPORTS_DIR / output_name

    try:
        result = build_video(
            script=script,
            output_path=output_path,
            image_paths=image_paths,
            aspect_ratio=ratio,
            wrap_chars=wrap_chars,
            include_subtitles=include_subtitles,
            elevenlabs_api_key=elevenlabs_key,
            elevenlabs_voice_id=voice_id,
        )
    except VideoBuildError as exc:
        return jsonify({"ok": False, "message": str(exc)}), 500

    return jsonify(
        {
            "ok": True,
            "message": result.message,
            "download_url": f"/exports/{output_name}",
            "audio_url": f"/exports/{result.audio_filename}" if result.audio_filename else None,
            "tts_enabled": result.tts_enabled,
            "used_uploaded_images": bool(image_paths),
        }
    )


@app.get("/exports/<path:filename>")
def download_export(filename: str):
    return send_from_directory(EXPORTS_DIR, filename, as_attachment=True)


def _find_available_port(start_port: int) -> int:
    port = start_port
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                port += 1
                continue
            return port
    raise RuntimeError("사용 가능한 로컬 포트를 찾지 못했습니다.")


def _open_browser(port: int) -> None:
    if os.environ.get("CLEANTUBE_NO_BROWSER") == "1":
        return
    url = f"http://127.0.0.1:{port}"
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()


if __name__ == "__main__":
    requested_port = int(os.environ.get("PORT", str(DEFAULT_PORT)))
    port = _find_available_port(requested_port)
    print(f"CleanTube Studio running at http://127.0.0.1:{port}")
    _open_browser(port)
    app.run(host="127.0.0.1", port=port, debug=False)
