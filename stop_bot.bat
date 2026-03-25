@echo off
chcp 65001 >nul
title S.T.A.L.K.E.R. Bot - Stop

echo ========================================
echo   S.T.A.L.K.E.R. Bot - STOP
echo ========================================
echo.

echo [INFO] Stopping bot...

REM Kill all python processes
taskkill /F /IM python.exe >nul 2>&1

REM Close the log window
taskkill /F /FI "WINDOWTITLE eq S.T.A.L.K.E.R. Bot - Log*" >nul 2>&1

echo.
echo [OK] Bot stopped
echo.

pause
