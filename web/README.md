# DIY Karaoke web app

One app for Windows and Mac — the web version of mix2k / mix2kmac /
mix2k_dragdrop / mix2kmac_dragdrop / 12k / 12kmac. It runs on your
own computer and you use it in the browser at
http://127.0.0.1:8001 (port 8001, so it does not clash with the
KTVOCR web UI on port 8000).

## How to run

**Windows** — double-click `start-windows.bat`.
Or in a terminal, from this folder:

```
py -3.11 -m pip install -r requirements.txt
py -3.11 main.py
```

**Mac** — double-click `start-mac.command`.
Or in Terminal, from this folder:

```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 main.py
```

The first run installs the Python packages (fastapi, uvicorn,
imageio-ffmpeg). On a Mac the packages go into a virtual
environment (`.venv` inside this folder) because macOS Python
refuses system-wide pip installs (PEP 668, "externally managed
environment"); `start-mac.command` creates that venv for you
automatically, so double-clicking it is the easiest route.

First time on a Mac, double-clicking a `.command` file may ask
for confirmation — right-click it, choose Open With > Terminal,
or run `chmod +x start-mac.command` once in Terminal.

## How to use

Two modes, picked at the top of the page:

1. **Mix 混音** — video + instrumental track. Drag the video
   (歌影) and the audio (伴奏) into the boxes, or click a box to
   browse. Builds the stereo karaoke file: instrumental left,
   original vocal right (左伴右唱).
2. **12k** — video only. Separates the instrumental first,
   then mixes. Pick the engine on the page: **UVR** (default —
   the same MDX-Net models the UVR5 GUI uses, via the
   `audio-separator` package; model picker offers Inst HQ 3,
   Karaoke 2, Inst HQ 4) or **Demucs**. Either engine is
   installed separately — see below.

Instead of uploading, you can paste a file's full path in the
box under each drop zone. Pasted paths are read directly from
this computer, so big videos do not need to upload. Uploaded
files go to `web/work/` while a job runs.

The finished `.mkv` is saved next to the video, and a Download
button appears on the page when the job finishes. A progress bar
shows the real ffmpeg progress.

## What it needs

- **Python 3.11** (Windows: `py -3.11`; Mac: python3 from
  python.org). The packages install themselves on first run
  (Windows: system pip; Mac: into a `.venv` folder, see above).
- The `web/` folder works on its own: it carries a bundled copy
  of `src/karaoke_common.py` (see the note at the top of that
  file). If you downloaded the whole repo, the app prefers the
  `src/` copy; if you only downloaded `web/`, the bundled copy
  is used. Either way, no extra files are needed.
- **ffmpeg** — bundled automatically via imageio-ffmpeg; no
  separate install needed. The status line on the page shows
  whether it was found.
- **UVR (audio-separator)** — only for 12k mode with the UVR
  engine, and still not bundled (torch + onnxruntime are far
  too big to bundle). The first 12k run downloads the chosen
  UVR model (~60 MB) once and reuses it afterwards. Install it
  into the web app's own venv so the page finds it:
  - Windows — install CPU torch first, otherwise pip fetches
    the ~2 GB CUDA torch:
    ```
    py -3.11 -m pip install torch --index-url https://download.pytorch.org/whl/cpu
    py -3.11 -m pip install "audio-separator[cpu]"
    ```
  - Mac — from the `web/` folder (uses its `.venv`):
    ```
    .venv/bin/python -m pip install "audio-separator[cpu]"
    ```
    On Apple Silicon this needs PyTorch 2.13+ and macOS 14+.
    The page shows whether UVR is ready; if it is not, 12k
    mode explains how to install it.
- **Demucs** — only for 12k mode with the Demucs engine, and
  still not bundled (bundling it makes a ~330 MB app that
  takes 2–3 minutes to start). Install it with
  `py -3.11 -m pip install demucs` (Windows) or
  `pip install demucs` (Mac). The page shows whether Demucs is
  ready; if it is not, 12k mode explains how to install it.

## Notes

- The server only listens on 127.0.0.1 — this computer. It is
  not reachable from your network.
- Jobs run one at a time in the order you start them.
- The desktop apps in `app/` still exist and still work; the
  web app is the same code underneath (it imports the shared
  `src/karaoke_common.py`), just with a browser UI instead of
  a separate Windows .exe and Mac .app.
