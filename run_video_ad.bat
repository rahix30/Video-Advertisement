@echo off
:loop
python video_player.py
timeout /t 3600 /nobreak
goto loop 