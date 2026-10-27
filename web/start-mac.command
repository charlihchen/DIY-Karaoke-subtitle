#!/bin/bash
# DIY Karaoke web app -- double-click to start (Mac).
# Creates a virtual environment the first time (macOS Python
# refuses system-wide pip installs -- PEP 668 -- so packages go
# into web/.venv instead), installs the packages, then starts
# the server and opens the app in your browser.
# First time only: right-click this file, choose Open With > Terminal,
# or run: chmod +x start-mac.command
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo "Creating virtual environment (.venv) -- first run only..."
  python3 -m venv .venv
fi
.venv/bin/python -c "import fastapi, uvicorn, imageio_ffmpeg" 2>/dev/null || .venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
