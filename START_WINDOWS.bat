@echo off
chcp 65001 >nul
title Hay Day 1.5.42 Server
cd /d "%~dp0"

echo [*] Installing requirements...
python -m pip install -q -r requirements.txt

echo [*] Detecting LAN IP...
python setup_host.py

echo.
echo ================================================
echo   SERVER STARTS NOW. Keep this window OPEN.
echo   Play Hay Day on your phone (same Wi-Fi).
echo   Press Ctrl+C to stop.
echo ================================================
echo.

python Main.py
pause
