@echo off
call "D:\MoveMunFunFresh\MyMediapipe\env\Scripts\activate.bat"
python D:\MoveMunFunFresh\MyMediapipe\MediapipeBodyTracker.py
echo Close in 2 Seconds
TIMEOUT /T 2 /NOBREAK
exit