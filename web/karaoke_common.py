"""Shared helpers for the DIY-Karaoke-subtitle apps.

NOTE: this file is a copy of ``src/karaoke_common.py``, bundled
here so the web folder works when downloaded on its own (without
the rest of the repo). Do not edit this copy directly -- edit
``src/karaoke_common.py`` and copy it here. When the full repo is
present, ``web/main.py`` prefers the src/ copy; this copy is only
used as a fallback.

Every app in this folder (mix2k, mix2kmac, mix2k_dragdrop,
mix2kmac_dragdrop, 12k, 12kmac) imports this module, and so does
the web app in ``web/``. PyInstaller includes it automatically
because it is a plain import in the same directory.

What it fixes over the original scripts:

* ffmpeg discovery: the originals called plain ``ffmpeg`` and only
  worked if ffmpeg was on PATH or sitting next to the .exe. The
  apps now try, in order: (1) the static ffmpeg bundled with the
  app via imageio-ffmpeg, (2) an ffmpeg binary sitting next to
  the app/exe, (3) ffmpeg on PATH. If none is found the user gets
  a dialog that says exactly how to fix it, instead of a bare
  "returned non-zero exit status" error.
* Output location: the originals wrote the .mkv into the current
  working directory, which for a double-clicked app is
  unpredictable (often the user's home folder). Output now goes
  next to the source video, where the user expects it.
* The GUI no longer freezes while ffmpeg/demucs runs: the work
  runs in a background thread with a status line, and the Mix
  button is disabled until it finishes.
* Errors show ffmpeg's own last lines, so a failure is diagnosable.
* 12k no longer has a hardcoded ``C:\\Users\\charl\\...`` path
  for demucs; it looks for ``demucs`` on PATH and explains how
  to install it when it is missing. Demucs itself is NOT bundled
  (bundling it makes a ~330 MB exe that takes 2-3 minutes to
  start -- see README), so 12k still needs a Python install
  with ``pip install demucs``.
"""

import os
import shutil
import subprocess
import sys
import threading

# File-dialog filters. NOTE: tkinter on Windows accepts "*.mp4;*.mkv"
# in one pattern, but macOS/Linux need one pattern per tuple, so
# every format gets its own entry -- this works everywhere.
VIDEO_TYPES = [
    ("MP4 Files", "*.mp4"),
    ("MKV Files", "*.mkv"),
    ("MPG Files", "*.mpg"),
    ("AVI Files", "*.avi"),
    ("All Video Files", "*.mp4 *.mkv *.mpg *.avi"),
]
AUDIO_TYPES = [
    ("MP3 Files", "*.mp3"),
    ("M4A Files", "*.m4a"),
    ("All Audio Files", "*.mp3 *.m4a"),
]
VIDEO_EXTS = (".mp4", ".mkv", ".mpg", ".avi")
AUDIO_EXTS = (".mp3", ".m4a")


def _exe_dir():
    """Directory holding the running script, or the frozen exe."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _app_parent_dir():
    """For a macOS .app bundle, the folder containing the .app.

    sys.executable is .../Name.app/Contents/MacOS/Name, so the
    parent of the .app is four levels up. Returns None when the
    executable is not inside a .app bundle.
    """
    if getattr(sys, "frozen", False) and sys.platform == "darwin":
        exe = sys.executable
        if ".app/Contents/MacOS/" in exe:
            return os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(exe)))
            )
    return None


def _bundled_ffmpeg():
    """Static ffmpeg shipped inside the app via imageio-ffmpeg."""
    try:
        import imageio_ffmpeg
    except ImportError:
        return None
    try:
        path = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None
    if path and os.path.isfile(path):
        return path
    return None


def find_ffmpeg():
    """Locate an ffmpeg executable. Returns the path, or None."""
    candidates = []
    bundled = _bundled_ffmpeg()
    if bundled:
        candidates.append(bundled)
    exe_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    exe_dir = _exe_dir()
    candidates.append(os.path.join(exe_dir, exe_name))
    parent = _app_parent_dir()
    if parent:
        candidates.append(os.path.join(parent, exe_name))
    for path in candidates:
        if path and os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return shutil.which("ffmpeg")


def ffmpeg_missing_message():
    if os.name == "nt":
        return (
            "FFmpeg was not found.\n\n"
            "The app normally ships with its own ffmpeg. If you built "
            "this copy yourself, either:\n"
            "- put ffmpeg.exe in the same folder as this app, or\n"
            "- install ffmpeg and add it to PATH.\n\n"
            "Get ffmpeg at https://www.gyan.dev/ffmpeg/builds/ "
            "(ffmpeg-git-full.7z) or https://github.com/BtbN/FFmpeg-Builds/releases/"
        )
    if sys.platform == "darwin":
        return (
            "FFmpeg was not found.\n\n"
            "The app normally ships with its own ffmpeg. If you built "
            "this copy yourself, either:\n"
            "- put the ffmpeg binary in the same folder as this app, or\n"
            "- install it with Homebrew: brew install ffmpeg"
        )
    return (
        "FFmpeg was not found.\n\n"
        "Install it with your package manager "
        "(e.g. sudo apt install ffmpeg) or put the ffmpeg binary "
        "in the same folder as this app."
    )


def find_demucs():
    """Locate the demucs command. Returns the path, or None."""
    return shutil.which("demucs")


def demucs_missing_message():
    if os.name == "nt":
        return (
            "Demucs was not found.\n\n"
            "12k needs Demucs installed separately (it is too big to "
            "bundle into the app). On your PC, open a terminal and run:\n\n"
            "    py -3.11 -m pip install demucs\n\n"
            "That needs Python 3.11 installed first. After installing, "
            "run this app again. FFmpeg is still needed as well."
        )
    if sys.platform == "darwin":
        return (
            "Demucs was not found.\n\n"
            "12k needs Demucs installed separately (it is too big to "
            "bundle into the app). On your Mac, open Terminal and run:\n\n"
            "    pip install demucs\n\n"
            "That needs Python 3 installed first. After installing, "
            "run this app again. FFmpeg is still needed as well."
        )
    return (
        "Demucs was not found.\n\n"
        "12k needs Demucs installed separately. Install it with:\n\n"
        "    pip install demucs\n\n"
        "Then run this app again."
    )


def karaoke_output_path(video_file, spaced=True):
    """Output .mkv path, next to the source video.

    ``spaced`` keeps each app's original naming: mix2k uses
    "Name (DIY KTV).mkv", 12k uses "Name(DIY KTV).mkv".
    """
    folder = os.path.dirname(os.path.abspath(video_file))
    stem = os.path.splitext(os.path.basename(video_file))[0]
    name = f"{stem} (DIY KTV).mkv" if spaced else f"{stem}(DIY KTV).mkv"
    return os.path.join(folder, name)


def tail_lines(text, count=8):
    """Last non-empty lines of ffmpeg output, for error dialogs."""
    if not text:
        return ""
    lines = [ln for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines[-count:])


class BackgroundJob:
    """Run a long command off the UI thread.

    ``work`` runs in a thread and returns (ok, message). When it
    finishes, ``done`` is called back on the Tk main thread via
    ``root.after`` polling (never touching Tk from the worker).
    While the job runs, ``status`` shows progress text and the
    given buttons are disabled.
    """

    def __init__(self, root, status_label, buttons):
        self.root = root
        self.status_label = status_label
        self.buttons = buttons
        self.thread = None
        self.result = None

    def start(self, status_text, work, done):
        if self.thread is not None and self.thread.is_alive():
            return False
        self.status_label.config(text=status_text)
        for btn in self.buttons:
            btn.config(state="disabled")
        self.result = None

        def _run():
            try:
                self.result = work()
            except Exception as exc:  # noqa: BLE001 - report to UI
                self.result = (False, f"Unexpected error: {exc}")

        self.thread = threading.Thread(target=_run, daemon=True)
        self.thread.start()
        self._poll(done)
        return True

    def _poll(self, done):
        if self.thread.is_alive():
            self.root.after(200, lambda: self._poll(done))
            return
        for btn in self.buttons:
            btn.config(state="normal")
        self.status_label.config(text="")
        ok, message = self.result if self.result else (False, "No result.")
        done(ok, message)


def media_duration(ffmpeg, path):
    """Duration of a media file in seconds, via ``ffmpeg -i``.

    Uses ffmpeg itself (not ffprobe) because the bundled static
    ffmpeg from imageio-ffmpeg ships no ffprobe binary.
    Returns None when the duration cannot be read.
    """
    import re

    try:
        proc = subprocess.run(
            [ffmpeg, "-i", path],
            capture_output=True,
            text=True,
            creationflags=(
                subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            ),
        )
    except (FileNotFoundError, OSError):
        return None
    match = re.search(r"Duration: (\d+):(\d+):([\d.]+)", proc.stderr or "")
    if not match:
        return None
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def _parse_ffmpeg_time(text):
    """Parse an ffmpeg ``time=HH:MM:SS.xx`` stamp to seconds."""
    import re

    match = re.search(r"time=(\d+):(\d+):([\d.]+)", text or "")
    if not match:
        return None
    hours, minutes, seconds = match.groups()
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def run_ffmpeg_progress(args, total_seconds=None, on_progress=None):
    """Run ffmpeg, reporting progress. Returns (ok, message).

    ``on_progress`` is called with a 0.0-1.0 fraction whenever
    ffmpeg reports a new ``time=`` stamp (only when the total
    duration is known). Used by the web app for a real progress
    bar; the desktop apps use plain :func:`run_ffmpeg`.
    """
    try:
        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            creationflags=(
                subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            ),
        )
    except FileNotFoundError:
        return False, "FFmpeg executable was not found."
    stderr_lines = []
    try:
        for line in proc.stderr:
            stderr_lines.append(line)
            if on_progress and total_seconds:
                current = _parse_ffmpeg_time(line)
                if current is not None:
                    on_progress(min(current / total_seconds, 1.0))
        proc.wait()
    except Exception as exc:  # noqa: BLE001 - report to caller
        proc.kill()
        return False, f"FFmpeg failed to run: {exc}"
    if proc.returncode == 0:
        return True, "Done."
    detail = tail_lines("".join(stderr_lines))
    return False, f"FFmpeg failed (exit {proc.returncode}).\n{detail}"


def run_ffmpeg(args, timeout=None):
    """Run ffmpeg, capturing output. Returns (ok, message)."""
    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=(
                subprocess.CREATE_NO_WINDOW
                if os.name == "nt"
                else 0
            ),
        )
    except FileNotFoundError:
        return False, "FFmpeg executable was not found."
    except subprocess.TimeoutExpired:
        return False, "FFmpeg timed out."
    if proc.returncode == 0:
        return True, "Done."
    detail = tail_lines(proc.stderr) or tail_lines(proc.stdout)
    return False, f"FFmpeg failed (exit {proc.returncode}).\n{detail}"


def separate_vocals_and_mix(ffmpeg, demucs, video_file, output_file,
                            on_stage=None, on_progress=None):
    """12k pipeline: extract wav -> Demucs -> mix. Returns (ok, message).

    All temporary files live in a temp dir that is always cleaned
    up, even when a step fails (the original left the .wav behind
    whenever Demucs failed). The instrumental track is found with
    a glob, because the model folder name depends on the Demucs
    version (htdemucs, htdemucs_ft, ...).

    ``on_stage`` is called with a short status string at each
    step and ``on_progress`` with a 0.0-1.0 fraction during the
    final mix (both optional; the desktop apps pass neither).
    """
    import glob
    import tempfile

    stem = os.path.splitext(os.path.basename(video_file))[0]
    workdir = tempfile.mkdtemp(prefix="ktv12k_")
    try:
        if on_stage:
            on_stage("Extracting audio from the video...")
        wav_file = os.path.join(workdir, f"{stem}.wav")
        ok, message = run_ffmpeg([ffmpeg, "-y", "-i", video_file, wav_file])
        if not ok:
            return False, f"Could not extract audio from the video.\n{message}"

        if on_stage:
            on_stage("Separating vocals with Demucs (this takes a few minutes)...")
        demucs_out = os.path.join(workdir, "demucs_output")
        os.makedirs(demucs_out, exist_ok=True)
        try:
            proc = subprocess.run(
                [demucs, "--two-stems=vocals", "-o", demucs_out,
                 "--mp3", wav_file],
                capture_output=True,
                text=True,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
                ),
            )
        except FileNotFoundError:
            return False, "Demucs executable was not found."
        if proc.returncode != 0:
            detail = tail_lines(proc.stderr) or tail_lines(proc.stdout)
            return False, f"Demucs failed (exit {proc.returncode}).\n{detail}"

        matches = glob.glob(
            os.path.join(demucs_out, "**", "no_vocals.mp3"), recursive=True
        )
        if not matches:
            return False, (
                "Demucs finished but no instrumental file "
                "(no_vocals.mp3) was found in its output."
            )
        instrumental = matches[0]

        if on_stage:
            on_stage("Mixing video + instrumental...")
        total = media_duration(ffmpeg, video_file)
        return run_ffmpeg_progress([
            ffmpeg,
            "-y",
            "-i", video_file,
            "-i", instrumental,
            "-map", "0:v",
            "-filter_complex",
            "[1:a][0:a]amerge=inputs=2,pan=stereo|c0<c0+c1|c1<c2+c3[a]",
            "-map", "[a]",
            output_file,
        ], total_seconds=total, on_progress=on_progress)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
