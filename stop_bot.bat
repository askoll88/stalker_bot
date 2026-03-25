@echo off
chcp 65001 >nul
title S.T.A.L.K.E.R. Bot - Stop

echo ========================================
echo   S.T.A.L.K.E.R. Bot - STOP
echo ========================================
echo.

echo [INFO] Stopping bot...

REM Find and stop python processes with main.py
for /f "tokens=5" %%a in ('wmic process where "name='python.exe'" get processid^,commandline 2^>nul ^| findstr "main.py"') do (
    echo [OK] Stopping process PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill all python processes if nothing found
taskkill /F /IM python.exe >nul 2>&1

echo.
echo [OK] Bot stopped
echo.

pause
