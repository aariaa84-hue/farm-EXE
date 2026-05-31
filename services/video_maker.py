from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import textwrap
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


class VideoBuildError(RuntimeError):
    pass


@dataclass(frozen=True)
class VideoResult:
    message: str
    tts_enabled: bool
    audio_filename: str | None = None


def _ffmpeg_exe() -> str:
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # pragma: no cover - depends on packaged runtime
        raise VideoBuildError(
            "FFmpeg를 찾을 수 없습니다. requirements 설치 또는 시스템 FFmpeg 설치를 확인해주세요."
        ) from exc


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/malgunbd.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def _dimensions(aspect_ratio: str) -> tuple[int, int]:
    if aspect_ratio == "9:16":
        return 1080, 1920
    return 1920, 1080


def _wrap_korean_friendly(text: str, chars: int) -> list[str]:
    paragraphs = [line.strip() for line in text.splitlines() if line.strip()]
    lines: list[str] = []
    for paragraph in paragraphs:
        lines.extend(textwrap.wrap(paragraph, width=chars, break_long_words=True))
    return lines or [text[:chars]]


def _chunks(lines: list[str], chunk_size: int = 3) -> list[list[str]]:
    return [lines[index : index + chunk_size] for index in range(0, len(lines), chunk_size)]


def _fit_background(image_path: Path, size: tuple[int, int]) -> Image.Image:
    with Image.open(image_path) as source:
        source = ImageOps.exif_transpose(source).convert("RGB")
        return ImageOps.fit(source, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def _base_slide(index: int, size: tuple[int, int]) -> Image.Image:
    width, height = size
    palette = [
        ((22, 30, 39), (61, 84, 106)),
        ((37, 51, 45), (93, 121, 93)),
        ((48, 42, 55), (118, 91, 126)),
        ((56, 47, 36), (132, 111, 77)),
    ]
    top, bottom = palette[index % len(palette)]
    image = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / max(1, height - 1)
        color = tuple(int(top[channel] * (1 - t) + bottom[channel] * t) for channel in range(3))
        draw.line([(0, y), (width, y)], fill=color)
    return image


def _draw_center_text(image: Image.Image, lines: list[str], subtitle_mode: bool) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    width, height = image.size
    if subtitle_mode:
        font = _font(max(34, int(width * 0.035)))
        line_gap = int(width * 0.012)
        margin = int(width * 0.08)
        text_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in lines)
        box_height = text_height + line_gap * max(0, len(lines) - 1) + int(width * 0.045)
        y = height - box_height - int(height * 0.07)
        draw.rounded_rectangle(
            (margin, y, width - margin, y + box_height),
            radius=18,
            fill=(0, 0, 0, 150),
        )
        y += int(width * 0.022)
    else:
        font = _font(max(44, int(width * 0.045)))
        line_gap = int(width * 0.014)
        text_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in lines)
        y = (height - text_height - line_gap * max(0, len(lines) - 1)) // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 190))
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 245))
        y += (bbox[3] - bbox[1]) + line_gap


def _make_slides(
    script: str,
    image_paths: list[Path],
    aspect_ratio: str,
    wrap_chars: int,
    include_subtitles: bool,
    temp_dir: Path,
) -> list[Path]:
    size = _dimensions(aspect_ratio)
    lines = _wrap_korean_friendly(script, wrap_chars)
    slide_texts = _chunks(lines)
    slide_count = max(len(slide_texts), len(image_paths), 1)
    slides: list[Path] = []

    for index in range(slide_count):
        if image_paths:
            image = _fit_background(image_paths[index % len(image_paths)], size)
        else:
            image = _base_slide(index, size)

        text_lines = slide_texts[index % len(slide_texts)]
        if include_subtitles or not image_paths:
            _draw_center_text(image, text_lines, subtitle_mode=include_subtitles and bool(image_paths))

        slide_path = temp_dir / f"slide_{index:03d}.jpg"
        image.save(slide_path, quality=92)
        slides.append(slide_path)

    return slides


def _estimate_duration(script: str, slide_count: int) -> float:
    seconds = max(6.0, len(script.replace(" ", "")) / 7.5)
    return max(seconds, slide_count * 3.0)


def _write_concat_file(slides: list[Path], duration_per_slide: float, concat_path: Path) -> None:
    lines: list[str] = []
    for slide in slides:
        safe_path = slide.as_posix().replace("'", "'\\''")
        lines.append(f"file '{safe_path}'")
        lines.append(f"duration {duration_per_slide:.3f}")
    safe_last = slides[-1].as_posix().replace("'", "'\\''")
    lines.append(f"file '{safe_last}'")
    concat_path.write_text("\n".join(lines), encoding="utf-8")


def _generate_tts(script: str, api_key: str, voice_id: str, output_path: Path) -> bool:
    if not api_key:
        return False

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = {
        "text": script,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.8},
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            output_path.write_bytes(response.read())
        return output_path.exists() and output_path.stat().st_size > 0
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")[:300]
        raise VideoBuildError(f"ElevenLabs 음성 생성에 실패했습니다. API 키와 Voice ID를 확인해주세요. {detail}") from exc
    except urllib.error.URLError as exc:
        raise VideoBuildError("ElevenLabs 서버에 연결하지 못했습니다. 네트워크 상태를 확인해주세요.") from exc


def _run_ffmpeg(slides: list[Path], output_path: Path, audio_path: Path | None, duration: float) -> None:
    ffmpeg = _ffmpeg_exe()
    concat_path = slides[0].parent / "slides.txt"
    duration_per_slide = max(2.0, duration / len(slides))
    _write_concat_file(slides, duration_per_slide, concat_path)

    command = [
        ffmpeg,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_path),
    ]
    if audio_path:
        command.extend(["-i", str(audio_path)])

    command.extend(
        [
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-r",
            "30",
            "-movflags",
            "+faststart",
        ]
    )
    if audio_path:
        command.extend(["-c:a", "aac", "-b:a", "192k", "-shortest"])
    else:
        command.extend(["-t", f"{duration:.3f}", "-an"])
    command.append(str(output_path))

    process = subprocess.run(command, capture_output=True, text=True)
    if process.returncode != 0:
        raise VideoBuildError(f"FFmpeg 영상 생성에 실패했습니다.\n{process.stderr[-1200:]}")


def build_video(
    script: str,
    output_path: Path,
    image_paths: list[Path],
    aspect_ratio: str,
    wrap_chars: int,
    include_subtitles: bool,
    elevenlabs_api_key: str,
    elevenlabs_voice_id: str,
) -> VideoResult:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="cleantube_") as temp_name:
        temp_dir = Path(temp_name)
        audio_path = temp_dir / "voice.mp3"
        tts_enabled = _generate_tts(script, elevenlabs_api_key, elevenlabs_voice_id, audio_path)
        slides = _make_slides(script, image_paths, aspect_ratio, wrap_chars, include_subtitles, temp_dir)
        duration = _estimate_duration(script, len(slides))
        _run_ffmpeg(slides, output_path, audio_path if tts_enabled else None, duration)
        if tts_enabled:
            final_audio_path = output_path.with_suffix(".mp3")
            shutil.copy2(audio_path, final_audio_path)
        else:
            final_audio_path = None

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise VideoBuildError("영상 파일이 생성되지 않았습니다.")

    if tts_enabled:
        message = "영상과 ElevenLabs mp3 음성이 생성되었습니다."
    else:
        message = "ElevenLabs API 키가 없어 TTS 없이 임시 영상만 생성되었습니다."
    return VideoResult(
        message=message,
        tts_enabled=tts_enabled,
        audio_filename=final_audio_path.name if final_audio_path else None,
    )
