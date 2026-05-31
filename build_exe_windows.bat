@echo off
chcp 65001 >nul
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  set PY=py
) else (
  set PY=python
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Creating virtual environment...
  %PY% -m venv .venv
  if errorlevel 1 goto error
)

echo [2/4] Installing requirements and PyInstaller...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto error

echo [3/4] Building EXE...
".venv\Scripts\python.exe" -m PyInstaller ^
  --noconfirm ^
  --onefile ^
  --console ^
  --name CleanTubeStudio ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --add-data "prompts;prompts" ^
  app.py
if errorlevel 1 goto error

echo [4/4] Done.
echo EXE path: %cd%\dist\CleanTubeStudio.exe
pause
goto end

:error
echo.
echo Build failed. Make sure Python 3.10+ is installed and the current folder is writable.
pause

:end
