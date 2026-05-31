@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv
)
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pyinstaller --noconfirm --clean --name "CleanTubeStudio" --add-data "templates;templates" --add-data "static;static" --hidden-import imageio_ffmpeg --collect-binaries imageio_ffmpeg app.py
