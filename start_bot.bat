@echo off
chcp 65001 >nul
title S.T.A.L.K.E.R. Bot

echo ========================================
echo   S.T.A.L.K.E.R. Bot - START
echo ========================================
echo.

cd /d "%~dp0"

REM Check Python
py --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Install Python: https://python.org
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check dependencies
echo [INFO] Checking dependencies...
py -m pip show vk-api >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    py -m pip install -r requirements.txt
)

echo.
echo ========================================
echo   STARTING BOT...
echo ========================================
echo.

REM Create logs folder
if not exist "logs" mkdir logs

echo [INFO] Bot is running...
echo [INFO] Press Ctrl+C to stop
echo.

REM Run bot in current window
py main.py

echo.
echo [INFO] Bot stopped
pause