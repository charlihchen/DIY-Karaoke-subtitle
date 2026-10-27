@echo off
REM DIY Karaoke web app -- double-click to start (Windows).
REM Installs the Python packages the first time, then starts the
REM server and opens the app in your browser.
cd /d %~dp0
py -3.11 -c "import fastapi, uvicorn, imageio_ffmpeg" 2>nul || py -3.11 -m pip install -r requirements.txt
py -3.11 main.py
pause
