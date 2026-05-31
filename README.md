# CleanTube Studio

Clean-room video creation tool for making MP4 drafts from a final script, optional uploaded images, and optional ElevenLabs TTS.

## Features

- Large final-script editor focused on video production.
- Optional ElevenLabs API key and Voice ID.
- TTS is disabled gracefully when no ElevenLabs API key is provided.
- Multiple local image uploads.
- Automatic placeholder background slides when no images are uploaded.
- Configurable subtitle line wrapping.
- 16:9 landscape and 9:16 portrait output.
- Optional burned-in subtitles.
- Final MP4 files saved in `exports/` and exposed as browser downloads.

## Run on Windows

```bat
run_windows.bat
```

The app starts at `http://127.0.0.1:5055` by default. If that port is already in use, it automatically tries `5056`, `5057`, and the next available local port, then opens the browser to the actual address.

## Build Windows EXE

```bat
build_exe_windows.bat
```

The GitHub Actions workflow in `.github/workflows/windows-exe.yml` builds the same PyInstaller executable on Windows.
