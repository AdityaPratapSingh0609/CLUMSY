@echo off
title Launching CLUMSY: your everyday AI...
color 0B

echo ============================================================
echo           CLUMSY: your everyday AI - App Launcher
echo ============================================================
echo Starting backend server and mesh networking on port 8080...
echo.

start "" /min python scripts/deploy_jarvis.py --port 8080

timeout /t 2 /nobreak >nul

if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app=http://127.0.0.1:8080
    exit
)

if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app=http://127.0.0.1:8080
    exit
)

start "" http://127.0.0.1:8080
exit
