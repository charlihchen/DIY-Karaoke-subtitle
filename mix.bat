@echo off
REM By Charlih Chen

SET CMD=%~1

IF "%CMD%" == "" (
  GOTO usage
)
ffmpeg.exe -i %1 -i %2 -map 0:v -filter_complex "[1:a][0:a]amerge=inputs=2,pan=stereo|c0<c0+c1|c1<c2+c3[a]" -map "[a]" %3

:usage
ECHO Mix
ECHO mix 需要使用三個參數: mix "歌曲.mp4" "伴奏.mp3" "輸出的KTV歌曲.mkv"
EXIT /B 1