"""DIY Karaoke web app -- one app for Windows and Mac.

Runs on your own computer and opens in the browser
(http://127.0.0.1:8001). Same two jobs as the desktop apps:

* Mix mode: pick a video (歌影) + an instrumental track (伴奏)
  and build a stereo karaoke file -- instrumental on the left
  channel, original (vocal) audio on the right ("左伴右唱").
* 12k mode: pick a video only. The app separates the
  instrumental with UVR (Ultimate Vocal Remover MDX-Net models,
  via the ``audio-separator`` package) by default, or with
  Demucs if you pick it. Either separator is installed
  separately -- see the status line on the page.

Files can be dragged into the browser (they upload to this
computer), or you can paste a path that already lives on this
computer -- pasted paths are read directly, so big videos do
not need to upload. Output is saved next to the video, and
you can also download it from the page.

ffmpeg ships with the app via imageio-ffmpeg, so no separate
ffmpeg install is needed. The server only listens on
127.0.0.1 (this computer), never on the network.

Run it:
    Windows:  double-click start-windows.bat  (or: py -3.11 main.py)
    Mac:      double-click start-mac.command  (or: python3 -m venv .venv
              && source .venv/bin/activate
              && python3 -m pip install -r requirements.txt
              && python3 main.py)
    (macOS Python refuses system-wide pip installs, so the Mac
    route uses a virtual environment; start-mac.command makes it.)
"""

import os
import shutil
import sys
import threading
import time
import uuid
import webbrowser

# Shared ffmpeg/demucs helpers live in src/ -- but the web folder
# is often downloaded on its own, so a copy is bundled here as
# web/karaoke_common.py. Prefer the canonical src/ copy when it
# exists (full repo checkout); otherwise fall back to the bundled
# one in this folder (already on sys.path as the script's dir).
_SRC_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "src"
)
if os.path.isfile(os.path.join(_SRC_DIR, "karaoke_common.py")):
    sys.path.insert(0, _SRC_DIR)
import karaoke_common as kc  # noqa: E402

from fastapi import FastAPI, File, Form, UploadFile  # noqa: E402
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse  # noqa: E402

PORT = 8001
HOST = "127.0.0.1"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = os.path.join(BASE_DIR, "work")
os.makedirs(WORK_DIR, exist_ok=True)

app = FastAPI(title="DIY Karaoke")

# job_id -> dict(status, stage, progress, message, output_path, output_name, mode, video_name)
JOBS = {}
JOBS_LOCK = threading.Lock()


def _venv_bin_dirs():
    """The web app's own .venv bin/Scripts dir, if it exists.

    Installing audio-separator into the web venv is the easiest
    Mac route (PEP 668 blocks system pip), so the app looks there
    as well as on PATH.
    """
    venv = os.path.join(BASE_DIR, ".venv")
    if os.name == "nt":
        return [os.path.join(venv, "Scripts")]
    return [os.path.join(venv, "bin")]


def _new_job(mode, video_name):
    job_id = uuid.uuid4().hex[:12]
    with JOBS_LOCK:
        JOBS[job_id] = {
            "id": job_id,
            "mode": mode,
            "video_name": video_name,
            "status": "running",
            "stage": "Starting...",
            "progress": 0.0,
            "message": "",
            "output_path": None,
            "output_name": None,
        }
    return job_id


def _update(job_id, **fields):
    with JOBS_LOCK:
        if job_id in JOBS:
            JOBS[job_id].update(fields)


def _finish(job_id, ok, message, output_path=None):
    fields = {
        "status": "done" if ok else "error",
        "progress": 1.0 if ok else JOBS[job_id]["progress"],
        "message": message,
    }
    if output_path:
        fields["output_path"] = output_path
        fields["output_name"] = os.path.basename(output_path)
    _update(job_id, **fields)


def _save_upload(upload, dest_path):
    with open(dest_path, "wb") as out:
        shutil.copyfileobj(upload.file, out, length=1024 * 1024)
    upload.file.close()


def _resolve_input(upload, path_text, work_path, label):
    """Return a local file path for an input.

    Either an uploaded file (saved to work_path) or a path pasted
    by the user that already exists on this computer.
    Returns (path, error_message).
    """
    if upload is not None and upload.filename:
        _save_upload(upload, work_path)
        return work_path, None
    path_text = (path_text or "").strip().strip('"').strip("'")
    if path_text:
        if os.path.isfile(path_text):
            return os.path.abspath(path_text), None
        return None, f"{label} not found: {path_text}"
    return None, f"Please provide a {label} (drop a file or paste its path)."


def _run_mix(job_id, video_file, audio_file):
    ffmpeg = kc.find_ffmpeg()
    if not ffmpeg:
        _finish(job_id, False, kc.ffmpeg_missing_message())
        return
    output_file = kc.karaoke_output_path(video_file, spaced=True)
    _update(job_id, stage="Mixing video + instrumental...")
    total = kc.media_duration(ffmpeg, video_file)

    def on_progress(frac):
        _update(job_id, progress=frac)

    ok, message = kc.run_ffmpeg_progress(
        [
            ffmpeg,
            "-y",
            "-i", video_file,
            "-i", audio_file,
            "-map", "0:v",
            "-filter_complex",
            "[1:a][0:a]amerge=inputs=2,pan=stereo|c0<c0+c1|c1<c2+c3[a]",
            "-map", "[a]",
            "-ac", "2",
            output_file,
        ],
        total_seconds=total,
        on_progress=on_progress,
    )
    if ok:
        _finish(job_id, True, f"Done! Output saved to:\n{output_file}", output_file)
    else:
        _finish(job_id, False, message)


def _venv_bin_dir():
    """The web app's own venv bin/Scripts dir, if it exists.

    ``start-mac.command`` / ``start-windows.bat`` install the
    web app's packages into ``web/.venv``; a separator installed
    there (e.g. ``audio-separator``) is usable even when it is
    not on PATH.
    """
    for path in _venv_bin_dirs():
        if os.path.isdir(path):
            return path
    return None


def _run_12k(job_id, video_file, backend="uvr", model=None):
    ffmpeg = kc.find_ffmpeg()
    if not ffmpeg:
        _finish(job_id, False, kc.ffmpeg_missing_message())
        return
    model = model or kc.UVR_DEFAULT_MODEL
    if model not in [m for m, _ in kc.UVR_MODELS]:
        model = kc.UVR_DEFAULT_MODEL
    output_file = kc.karaoke_output_path(video_file, spaced=False)

    def on_stage(text):
        _update(job_id, stage=text, progress=0.0)

    def on_progress(frac):
        # Final mix is the last third of the job.
        _update(job_id, progress=0.66 + 0.34 * frac)

    search_dirs = [d for d in [_venv_bin_dir()] if d]
    ok, message = kc.separate_and_mix(
        ffmpeg, video_file, output_file,
        backend=backend, model=model,
        demucs=kc.find_demucs(),
        audio_separator=kc.find_audio_separator(search_dirs),
        on_stage=on_stage, on_progress=on_progress,
    )
    if ok:
        _finish(job_id, True, f"Done! Output saved to:\n{output_file}", output_file)
    else:
        _finish(job_id, False, message)


@app.get("/", response_class=HTMLResponse)
def index():
    with open(os.path.join(BASE_DIR, "templates", "index.html"), encoding="utf-8") as fh:
        return fh.read()


@app.get("/api/status")
def status():
    ffmpeg = kc.find_ffmpeg()
    demucs = kc.find_demucs()
    uvr = kc.find_audio_separator([d for d in [_venv_bin_dir()] if d])
    return {
        "ffmpeg": bool(ffmpeg),
        "ffmpeg_path": ffmpeg or "",
        "demucs": bool(demucs),
        "demucs_path": demucs or "",
        "uvr": bool(uvr),
        "uvr_path": uvr or "",
        "uvr_models": [
            {"filename": fn, "label": label}
            for fn, label in kc.UVR_MODELS
        ],
        "uvr_default_model": kc.UVR_DEFAULT_MODEL,
    }


@app.get("/api/jobs")
def list_jobs():
    with JOBS_LOCK:
        jobs = sorted(JOBS.values(), key=lambda j: j["id"], reverse=True)
    return [
        {k: v for k, v in job.items() if k != "output_path"} for job in jobs[:20]
    ]


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if not job:
        return JSONResponse({"error": "Unknown job."}, status_code=404)
    return {k: v for k, v in job.items() if k != "output_path"}


@app.get("/api/download/{job_id}")
def download(job_id: str):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if not job or not job.get("output_path") or not os.path.isfile(job["output_path"]):
        return JSONResponse({"error": "Output not available."}, status_code=404)
    return FileResponse(job["output_path"], filename=job["output_name"])


@app.post("/api/mix")
def start_mix(
    mode: str = Form("mix"),
    backend: str = Form("uvr"),
    model: str = Form(""),
    video: UploadFile = File(None),
    audio: UploadFile = File(None),
    video_path: str = Form(""),
    audio_path: str = Form(""),
):
    if mode not in ("mix", "demucs"):
        return JSONResponse({"error": "Unknown mode."}, status_code=400)
    if backend not in ("uvr", "demucs"):
        backend = "uvr"
    job_id = _new_job(mode, (video.filename if video else "") or os.path.basename(video_path))
    job_dir = os.path.join(WORK_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    video_file, error = _resolve_input(
        video, video_path,
        os.path.join(job_dir, (video.filename if video and video.filename else "video")),
        "video file",
    )
    if error:
        _finish(job_id, False, error)
        return {"job_id": job_id}
    if mode == "mix":
        audio_file, error = _resolve_input(
            audio, audio_path,
            os.path.join(job_dir, (audio.filename if audio and audio.filename else "audio")),
            "audio file",
        )
        if error:
            _finish(job_id, False, error)
            return {"job_id": job_id}
        thread = threading.Thread(
            target=_run_mix, args=(job_id, video_file, audio_file), daemon=True
        )
    else:
        thread = threading.Thread(
            target=_run_12k, args=(job_id, video_file, backend, model),
            daemon=True,
        )
    thread.start()
    return {"job_id": job_id}


if __name__ == "__main__":
    import uvicorn

    def _open_browser():
        time.sleep(1)
        webbrowser.open(f"http://{HOST}:{PORT}")

    threading.Thread(target=_open_browser, daemon=True).start()
    print(f"DIY Karaoke web app: http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
