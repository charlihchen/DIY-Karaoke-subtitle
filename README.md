# DIY-Karaoke-subtitle
Making your own karaoke subtitle video for sing along at home use only. 

ffmpeg command to make the karaoke song with No Vocal on FL(Left channel) and Vocal with instrumental on FR(Right channel).

In chinese, we call it "左伴右唱".

Here is the sample command:
<code>
ffmpeg.exe -i "Youtube下載歌曲(導唱字幕)_KTV.mp4" -i "Youtube下載歌曲(伴奏)_instrumental.mp3" -map 0:v -filter_complex "[1:a][0:a]amerge=inputs=2,pan=stereo|c0<c0+c1|c1<c2+c3[a]" -map "[a]" "KTV_song歌曲(左伴右唱).mkv"
</code>

聽說正版的K歌都是右伴左唱，所以 the sample command:
<code>
ffmpeg.exe -i "Youtube下載歌曲(導唱字幕)_KTV.mp4" -i "Youtube下載歌曲(伴奏)_instrumental.mp3" -map 0:v -filter_complex "[0:a][1:a]amerge=inputs=2,pan=stereo|c0<c0+c1|c1<c2+c3[a]" -map "[a]" "KTV_song歌曲(右伴左唱).mkv"
</code>

Note:

寫了一個 mix.bat 檔來解決你遇到的格式輸出錯誤問題。

將mix.bat 檔放到 ffmpeg.exe 同一目錄下，然後在DOS command視窗中輸入:

mix.bat "歌曲.mp4" "伴奏.mp3" "輸出的KTV歌曲.mkv"

mix.bat 後的三個參數間請用空格分開喔. 每個參數用 " 符號括起來。
<hr class="dashed">
I recently discovered the "FFmpeg Batch AV converter" free GUI application for FFmpeg at https://github.com/eibols/ffmpeg_batch
<img width="1616" height="874" alt="image" src="https://github.com/user-attachments/assets/11eb7ad7-a0fe-4897-b155-405b29b17337" />
<hr class="dashed">
又寫了一個 mix2k.exe 檔來解決只習慣用GUI的人。

記得要將ffmpeg.exe檔跟它的所有 ?????.dll檔都放跟mix2k.exe在同一檔案夾中。

(Make sure to put ffmpeg.exe and all its .dll files to the same folder of the mix2k.exe)

Actually, there is ffmpeg.exe without .dll. You can download it at https://github.com/BtbN/FFmpeg-Builds/releases/

The ffmpeg.exe without .dll from the folder .\portable_version\bin\
You can download ffmpeg.exe portable version at https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z

mix2k.exe執行檔有些陽春，因為我非程式設計師；

它是微軟的copilot AI (類似ChatGPT)幫我生成的。

至少它能達到我想要的結果。

你們也可以試試 AI 的幫忙。

Note:

Just foud out 2 issues for those distributing .exe(for Windows OS) and .app(for Mac OS) files.

#1 issue: Windows OS will detect with malware for those mix2k.exe and mix2k_dragdrop.exe.

#2 issue: Mac OS won't able to run the distributed App once you donwloadeded it to your Mac.

Best Solution for the above issues is to run python on Terminal for those 3 py codes:

#1. Press "Windows" key and "X" key >> Select "Terminal" >> input python mix2k.py or python mix2k_dragdrop.py

#2. Press "Cmd" and "Space" >> input "terminal" on spotlight search box >> Press Enter >> inpot python mix2kmac.py

Note2:

$pip install pyinstaller

$pyinstaller --onefile mix2kmac.py

The mix2kmac App is under the "dist" folder.

The mix2kmac mixed output path is under /Users/yourMacAccountName/

Or using Finder >> Go >> Go to Folder... >> input "/Users" >> Enter >> YourMacAccountName

$pip install tkinterdnd2 for mix2kmac_dragdrop.py

<hr class="dashed">
12k.exe is created. Make sure the file run with ffmpeg.exe in the same folder. :)<br>
(12k.exe 已創建。確保 EXE 檔 跟 ffmpeg.exe 在同一資料夾中一起運行。)<br>
<pre>
Just test it myself on other PC without python installed and the 12k.exe is unable to call Demucs.
So, have to find a way to pack the Demucs into 12k.exe. Stay tune with newest 12k.exe then.
Gaveup the ideal of pack the Demucs into 12k.exe since it add-up file size from 9,713KB=9MB to 329,503KB=329MB.
The loading time for the 329MB 12k.exe is around 2 to 3 minutes. It is unacceptable!!!
</pre>
<pre>
  放棄將 Demucs lib 打包進 12k.exe 的理想來給這些不想安裝 Python 的使用者。
  因為打完包的 12k.exe 檔案大小增大到 329MB， 而且每次執行它要等 3 分鐘的 Demucs loading time(裝載時間)。
  所以還是請使用者乖乖的來安裝 Python 到你的電腦上吧。
  已經盡力將 12k.py 轉成 12k.exe 讓使用者省去打 python 12k.py 來執行 12k.py程式的動作。
  但使用者還是得學習 DOS command prompt 或 Anaconda Prompt 的操作環境。
  缺什麼就用 pip install 來裝什麼。
  ===============================
  例如, 執行完 python 12k.py
  上面錯誤(Error)說缺 Demucs
  那就用pip install demucs 來裝 demucs
  你的電腦 Python 環境裝這些 12k.py程式需求的module(模組)後；下次執行 12k.py程式就不需要再pip install ???了。
</pre>
The separating vocal and no-vocal by Demucs and mixing by ffmpeg,exe take time depend on your PC spec.<br>
(Demucs 的分離 vocal 和 no-vocal 以及 ffmpegexe 的混音處理需要一些時間，具體取決於您的 PC 規格。)<br>
Will try to create the same function App to run on MacOS M1/M2/M3. Guess that it will process faster with GPU then.<br>

![image](https://github.com/user-attachments/assets/b330353e-d654-4cbb-b8bc-3678364ab7b6)
<hr class="dotted">

Here is the "左伴右唱" diagram:

![image](https://github.com/user-attachments/assets/dcb1ff43-bbb7-4380-948a-20a41e6bd6bd)

The concept of the mix2k.exe in diagram:

![image](https://github.com/user-attachments/assets/5b6ea515-f388-4c03-af47-30843090e25e)

<a href="https://www.buymeacoffee.com/charlih" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

<hr class="dashed">

## The apps (built automatically)

The Python sources in `src/` are built into real apps by GitHub
Actions on every change — Windows `.exe` files and macOS `.app`
bundles, all in the `app/` folder (see `app/README.md` for how to
run them and the first-run warnings).

| App | Platform | What it does |
| --- | --- | --- |
| `mix2k.exe` | Windows | Video + instrumental → karaoke file |
| `mix2k_dragdrop.exe` | Windows | Same, with drag-and-drop |
| `12k.exe` | Windows | Video only — UVR (default) or Demucs separates the instrumental, then mixes |
| `mix2kmac.app` | macOS | Video + instrumental → karaoke file |
| `mix2kmac_dragdrop.app` | macOS | Same, with drag-and-drop / paste |
| `12kmac.app` | macOS | Video only — UVR (default) or Demucs separation + mix |

What changed in the reprogram (Oct 2026):

- ffmpeg is bundled inside every app (via imageio-ffmpeg), so you
  no longer need ffmpeg.exe next to the app.
- The output `.mkv` is saved next to the video you picked, not in
  whatever folder the app happened to start in.
- The window no longer freezes while a mix runs — there is a
  status line and a progress bar, and the Mix button is disabled
  until it finishes.
- Failures show ffmpeg's own error message instead of a bare
  "returned non-zero exit status".
- `12k` / `12kmac` no longer have a hardcoded
  `C:\Users\charl\...` Demucs path; they find Demucs on PATH and
  explain how to install it when it is missing. Temp files are
  always cleaned up, even when a step fails.
- `12k` / `12kmac` now separate with UVR (MDX-Net models, the
  same engine as the UVR5 GUI, via `audio-separator`) by
  default, with Demucs as a second choice and a model picker
  (Inst HQ 3, Karaoke 2, Inst HQ 4). The web app has the same
  choice.
- `mix2k_dragdrop2.py` was an exact duplicate of
  `mix2k_dragdrop.py` and was removed.

Two honest limits (unchanged):

1. The apps are not code-signed, so Windows SmartScreen and macOS
   Gatekeeper still warn on first run. Signing needs paid
   certificates (Windows) / a paid Apple Developer account
   ($99/year). Workarounds are in `app/README.md`.
2. `12k` / `12kmac` still need their separator installed
   separately — UVR (`pip install "audio-separator[cpu]"`,
   CPU torch first on Windows) or Demucs (`pip install
   demucs`) — bundling either makes a ~330 MB app that takes
   2–3 minutes to start.

The old `src/setup.py` / `src/setup2.py` (py2app) are superseded
by the PyInstaller + GitHub Actions build; they are kept for
reference only.

## Web app — one app for Windows and Mac

If you would rather not juggle a Windows .exe and a Mac .app,
there is now a web version in `web/` — the same mix and 12k
jobs, but you use it in the browser. One codebase, both systems.

```
Windows: double-click web/start-windows.bat
Mac:     double-click web/start-mac.command
```

It opens at http://127.0.0.1:8001. Drag the video and the
instrumental into the page (or paste their paths — pasted paths
are read straight from the computer, so big videos do not need
to upload), watch the real progress bar, and download the
finished file. See `web/README.md` for the full instructions.
The 12k mode needs its separator installed separately — UVR
(default) or Demucs; see `web/README.md`.

