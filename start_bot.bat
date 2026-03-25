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

REM Run bot in new window with logs
start "S.T.A.L.K.E.R. Bot - Log" /d "%~dp0" cmd /c "py main.py 2^>^&1 | tee logs\bot.log & pause"

echo [OK] Bot started in new window
echo Logs saved to: logs\bot.log
echo.
echo Run stop_bot.bat to stop the bot
echo.

pause
