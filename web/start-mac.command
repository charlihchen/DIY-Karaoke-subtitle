#!/bin/bash
# DIY Karaoke web app -- double-click to start (Mac).
# Installs the Python packages the first time, then starts the
# server and opens the app in your browser.
# First time only: right-click this file, choose Open With > Terminal,
# or run: chmod +x start-mac.command
cd "$(dirname "$0")"
python3 -c "import fastapi, uvicorn, imageio_ffmpeg" 2>/dev/null || python3 -m pip install -r requirements.txt
python3 main.py
