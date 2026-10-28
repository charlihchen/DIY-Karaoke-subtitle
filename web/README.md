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
2. **12k** — 1 click 2(to) K歌. Separates(**分離**成伴奏) the instrumental first
   with UVR (the same MDX-Net models the UVR5 GUI uses, via
   the `audio-separator` package; model picker offers Inst HQ 3,
   Karaoke 2, Inst HQ 4), then mixes(然後再跟原音樂檔**混音**). UVR is installed
   separately — see below.

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
- **UVR (audio-separator)** — only for 12k mode, and still
  not bundled (torch + onnxruntime are far too big to bundle). The first 12k run downloads the chosen
  UVR model (~60 MB) once and reuses it afterwards. Install it
  into the web app's own venv so the page finds it:
  - Windows — install CPU torch first, otherwise pip fetches
    the ~2 GB CUDA torch:
    ```
    py -3.11 -m pip install torch --index-url https://download.pytorch.org/whl/cpu
    py -3.11 -m pip install "audio-separator[cpu]" audioread
    ```
  - Mac — UVR needs its own Python 3.13 venv (your Mac's
    python3 is 3.15, and onnxruntime has no 3.15 version yet,
    so installing into the web app's `.venv` fails):
    ```
    brew install python@3.13
    /opt/homebrew/bin/python3.13 -m venv ~/uvr-env
    ~/uvr-env/bin/pip install torch "audio-separator[cpu]" audioread
    echo 'export PATH="$HOME/uvr-env/bin:$PATH"' >> ~/.zprofile
    ```
    Reopen Terminal afterwards so the PATH change takes effect.
    On Apple Silicon this needs PyTorch 2.13+ and macOS 14+.
    The page shows whether UVR is ready; if it is not, 12k
    mode explains how to install it.

## Notes

- The server only listens on 127.0.0.1 — this computer. It is
  not reachable from your network.
- Jobs run one at a time in the order you start them.
- The desktop apps in `app/` still exist and still work; the
  web app is the same code underneath (it imports the shared
  `src/karaoke_common.py`), just with a browser UI instead of
  a separate Windows .exe and Mac .app.

## Screenshot

<img width="1530" height="988" alt="image" src="https://github.com/user-attachments/assets/3c74a696-1867-493c-9b10-06973628de4a" />

## UVR 3 tracks explaination (HQ_3 vs. KARA_2 vs. HQ_4)
```
The UVR-MDX-NET-Inst_**HQ_3** model is recommended for karaoke tracks to keep the instrumental clean, 
while the UVR_MDXNET_**KARA_2** model is designed to remove harmony and leave only the lead vocal, 
and the UVR-MDX-NET-Inst_**HQ_4** model is noted for high-quality instrumental extraction with minimal vocal bleed.
```
```
製作卡拉 OK 伴奏軌時，建議使用 UVR-MDX-NET-Inst_**HQ_3** 模型以保持樂器音質純淨；
UVR_MDXNET_**KARA_2** 模型則是為了移除和聲並僅保留主唱聲部而設計；
而 UVR-MDX-NET-Inst_**HQ_4** 模型則以高品質的樂器提取及極低的人聲殘留著稱。
```

### Overview of UVR Models for Karaoke Tracks
```
When selecting a model for creating karaoke tracks using UVR, 
it's essential to understand the differences between the available options. 
Here’s a breakdown of the UVR models: 
UVR-MDX-NET-Inst_**HQ_3**, 
UVR_MDXNET_**KARA_2**, 
and UVR-MDX-NET-Inst_**HQ_4**.
```

(製作卡拉 OK 伴奏的 UVR 模型概覽)
```
使用 UVR 製作卡拉 OK 伴奏時，了解各個可用模型之間的差異至關重要。
以下是 UVR 模型的詳細分析：
1. UVR-MDX-NET-Inst_**HQ_3**
2. UVR_MDXNET_**KARA_2**
3. UVR-MDX-NET-Inst_**HQ_4**
```

### 3 Track Model Comparison (3個模型的比較)
| No |Model Name 	|Purpose	|Key Features |
|----|------------|--------|-------------|
| 1 |UVR-MDX-NET-Inst_**HQ_3** |Karaoke track (instrumental only)	|- Keeps the instrumental clean  |
| 2 |UVR_MDXNET_**KARA_2**	|Harmony removal (lead vocal only) 	|- Removes harmony while retaining lead vocals  |
| 3 |UVR-MDX-NET-Inst_**HQ_4**	|High-quality instrumental extraction 	|- Minimal vocal bleed, high fidelity  |

| 排次 | 模型名稱	| 用途 | 主要特點 |
|----|---------|------|---------|
| 1 |UVR-MDX-NET-Inst_**HQ_3** | 卡拉 OK 伴奏（僅純樂器）	| - 保持伴奏音軌乾淨 |
| 2 |UVR_MDXNET_**KARA_2**	| 人聲和聲移除（僅保留主唱）	|- 移除和聲並保留主唱人聲 |
| 3 |UVR-MDX-NET-Inst_**HQ_4**	|  高品質伴奏提取	|- 極少人聲殘留，高傳真度 |

### 3 detailed Model Functions (模型功能詳解)
1. UVR-MDX-NET-Inst_**HQ_3**
- Goal: Ideal for creating karaoke tracks by isolating the instrumental.
  目標：透過分離伴奏，打造理想的卡拉 OK 軌道。
- Strength: Maintains the integrity of the instrumental sound, ensuring a clean output suitable for karaoke.
  優點：保持伴奏音質的完整性，確保輸出清晰且適合卡拉 OK 使用。

2. UVR_MDXNET_**KARA_2**
- Goal: Focuses on removing harmony to leave only the lead vocal.
  目標：專注於移除和聲，僅保留主唱。
- Strength: Useful for users who want to isolate the lead vocal while eliminating background harmonies, making it suitable for a cappella arrangements.
  優點：適合想要分離主唱並消除背景和聲的使用者，非常適合用於阿卡貝拉（無伴奏合唱）編曲。

3. UVR-MDX-NET-Inst_**HQ_4**
- Goal: Designed for high-quality instrumental extraction.
  目標：專為高品質伴奏提取而設計。
- Strength: Offers minimal vocal bleed, ensuring that the instrumental remains rich and full, making it ideal for sampling or remixing.
  優點：人聲殘留極少，確保伴奏音質豐富飽滿，是取樣或混音的理想選擇。

### Conclusion (結論)
Choosing the right UVR model depends on your specific needs for karaoke tracks. 
For pure instrumental tracks, UVR-MDX-NET-Inst_**HQ_3** is recommended. 
If you need to isolate lead vocals while removing harmonies, UVR_MDXNET_**KARA_2** is the best choice. 
For high-quality instrumental extraction with minimal vocal interference, UVR-MDX-NET-Inst_**HQ_4** is the optimal option.

選擇合適的 UVR 模型取決於您對卡拉 OK 伴奏軌的具體需求。若需要純樂器軌，建議使用 UVR-MDX-NET-Inst_**HQ_3**。
如果您需要隔離主唱並去除和聲，UVR_MDXNET_**KARA_2** 是最佳選擇。
若要進行高品質的樂器提取並將人聲干擾降至最低，UVR-MDX-NET-Inst_**HQ_4** 則是理想之選。

