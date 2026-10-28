# The apps

These are built automatically by GitHub Actions on every change to
`src/` (see `.github/workflows/build-apps.yml`) and committed here,
so this folder always holds the latest builds.

## Windows — `app/windows/`

| App | What it does |
| --- | --- |
| `mix2k.exe` | Pick a video + an instrumental track, mix into a karaoke file (左伴右唱) |
| `mix2k_dragdrop.exe` | Same, but drag-and-drop the files in |
| `12k.exe` | Pick a video only — separates the instrumental with UVR, then mixes. Needs UVR installed separately (see below) |

Double-click to run. The output `.mkv` is saved next to the video
you picked. ffmpeg is bundled inside each app — no separate
ffmpeg install needed.

**First-run warning (expected):** the apps are not code-signed, so
Windows SmartScreen may say "Windows protected your PC". Click
**More info → Run anyway**. Signing would need a paid certificate.

## macOS — `app/mac/`

| App | What it does |
| --- | --- |
| `mix2kmac.app.zip` | Pick a video + an instrumental track, mix into a karaoke file |
| `mix2kmac_dragdrop.app.zip` | Same, but drag-and-drop (or Cmd-V paste a path) |
| `12kmac.app.zip` | Pick a video only — UVR separation + mix. Needs UVR installed separately (see below) |

Unzip, then drag the `.app` into Applications (or anywhere) and
double-click. The output `.mkv` is saved next to the video you
picked. ffmpeg is bundled inside each app.

**First-run warning (expected):** the apps are not code-signed, so
macOS Gatekeeper may refuse to open a downloaded app ("cannot be
opened because the developer cannot be verified" / "is damaged").
Workaround: right-click (or Control-click) the app → **Open** →
**Open**. If it still refuses, run this once in Terminal:

```
xattr -d com.apple.quarantine /Applications/mix2kmac.app
```

Signing would need a paid Apple Developer account ($99/year).

## 12k / 12kmac and UVR

`12k` / `12kmac` separate the vocal out of a song with UVR
(the same MDX-Net models the UVR5 GUI uses, via the
`audio-separator` package; the model picker offers Inst HQ 3,
Karaoke 2, Inst HQ 4), then mix. UVR is **not** bundled into
the app: bundling torch makes a ~330 MB file that takes 2–3
minutes to start, so the app checks for it and tells you how
to install it instead.

**UVR (audio-separator):**
- **Windows:** install Python 3.11, then in Terminal run
  CPU torch first (otherwise pip fetches the ~2 GB CUDA torch),
  then audio-separator:
  ```
  py -3.11 -m pip install torch --index-url https://download.pytorch.org/whl/cpu
  py -3.11 -m pip install "audio-separator[cpu]" audioread
  ```
- **macOS:** UVR needs its own Python 3.13 venv (Homebrew's
  python3 is 3.15, and onnxruntime has no 3.15 version yet).
  In Terminal run
  ```
  brew install python@3.13
  /opt/homebrew/bin/python3.13 -m venv ~/uvr-env
  ~/uvr-env/bin/pip install torch "audio-separator[cpu]" audioread
  ```
  Then make sure `audio-separator` is on PATH, e.g. add this
  line to `~/.zprofile` and reopen Terminal:
  ```
  export PATH="$HOME/uvr-env/bin:$PATH"
  ```

The first 12k run downloads the chosen UVR model (~60 MB)
once and reuses it afterwards.

After that, run the app again. UVR + ffmpeg do the heavy
lifting, so a song takes a few minutes depending on your
machine.

## Building locally (optional)

You don't need this — Actions builds the apps — but to build on
your own machine:

```
pip install pyinstaller imageio-ffmpeg tkinterdnd2
cd src
pyinstaller --onefile --windowed --name mix2k --collect-all imageio_ffmpeg mix2k.py
```

On macOS, drop `--onefile` to get a real `.app` bundle:

```
pyinstaller --windowed --name mix2kmac --collect-all imageio_ffmpeg mix2kmac.py
```

## 12K AKA. 1 click to(2) K檔

<img width="1149" height="779" alt="image" src="https://github.com/user-attachments/assets/5f4b463a-aeb6-4a96-a3ca-165fe274e35a" />

