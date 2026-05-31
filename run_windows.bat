@echo off
chcp 65001 >nul
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  set "PY=python"
)

%PY% --version >nul 2>nul
if errorlevel 1 goto python_error

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Creating virtual environment...
  %PY% -m venv .venv
  if errorlevel 1 goto error
)

echo [2/3] Installing requirements...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto error
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error

echo [3/3] Starting CleanTube Studio...
echo Browser will open at http://127.0.0.1:5055
".venv\Scripts\python.exe" app.py
goto end

:python_error
echo.
echo Python 3.10 or newer is required.
echo Install it from https://www.python.org/downloads/
pause
goto end

:error
echo.
echo Failed. Please check the message above, then run this file again.
pause

:end
