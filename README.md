# DIY-Karaoke-subtitle
Making your own karaoke subtitle video for sing along at home use only. 

ffmpeg command to make the karaoke song with No Vocal on FL(Left channel) and Vocal with instrumental on FR(Right channel).

In chinese, we call it "左伴右唱".

Here is the sample command:

ffmpeg.exe -i "Youtube下載歌曲(導唱字幕)_KTV.mp4" -i "Youtube下載歌曲(伴奏)_instrumental.mp3" -map 0:v -filter_complex "[1:a][0:a]amerge=inputs=2,pan=stereo|c0<c0+c1|c1<c2+c3[a]" -map "[a]" "KTV_song歌曲(左伴右唱).mkv"

Note:

寫了一個 mix.bat 檔來解決你遇到的格式輸出錯誤問題。

將mix.bat 檔放到 ffmpeg.exe 同一目錄下，然後在DOS command視窗中輸入:

mix.bat "歌曲.mp4" "伴奏.mp3" "輸出的KTV歌曲.mkv"

mix.bat 後的三個參數間請用空格分開喔. 每個參數用 " 符號括起來。

又寫了一個 mix2k.exe 檔來解決只習慣用GUI的人。

記得要將ffmpeg.exe檔跟它的所有 ?????.dll檔都放跟mix2k.exe在同一檔案夾中。

(Make sure to put ffmpeg.exe and all its .dll files to the same folder of the mix2k.exe)

![image](https://github.com/user-attachments/assets/28da4f02-a325-4880-9aa9-745737cc6f23)

mix2k.exe執行檔有些陽春，因為我非程式設計師；

它是微軟的copilot AI (類似ChatGPT)幫我生成的。

至少它能達到我想要的結果。

你們也可以試試 AI 的幫忙。

Here is the "左伴右唱" diagram:

![image](https://github.com/user-attachments/assets/dcb1ff43-bbb7-4380-948a-20a41e6bd6bd)
