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
<hr class="dashed">
12k.exe is created. Make sure the file run with ffmpeg.exe in the same folder. :)<br>
(12k.exe 已創建。確保 EXE 檔 跟 ffmpeg.exe 在同一資料夾中一起運行。)<br>

Just test it myself on other PC without python installed and the 12k.exe is unable to call Demucs<br>
So, have to find a way to pack the Demucs into 12k.exe. Stay tune with newest 12k.exe then.<br>

The separating vocal and no-vocal by Demucs and mixing by ffmpeg,exe take time depend on your PC spec.<br>
(Demucs 的分離 vocal 和 no-vocal 以及 ffmpegexe 的混音處理需要一些時間，具體取決於您的 PC 規格。)<br>
Will try to create the same function App to run on MacOS M1/M2/M3. Guess that it will process faster with GPU then.<br>
![image](https://github.com/user-attachments/assets/b330353e-d654-4cbb-b8bc-3678364ab7b6)
<hr class="dotted">

Here is the "左伴右唱" diagram:

![image](https://github.com/user-attachments/assets/dcb1ff43-bbb7-4380-948a-20a41e6bd6bd)

The concept of the mix2k.exe in diagram:

![image](https://github.com/user-attachments/assets/5b6ea515-f388-4c03-af47-30843090e25e)
