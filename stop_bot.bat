@echo off
chcp 65001 >nul
title S.T.A.L.K.E.R. Bot - Остановка

echo ========================================
echo   S.T.A.L.K.E.R. Bot - ОСТАНОВКА
echo ========================================
echo.

REM Останавливаем процессы Python, связанные с ботом
echo [INFO] Остановка бота...

REM Ищем и останавливаем процессы python с main.py
for /f "tokens=5" %%a in ('wmic process where "name='python.exe'" get processid^,commandline 2^>nul ^| findstr "main.py"') do (
    echo [OK] Остановка процесса PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

REM Если не нашли, пробуем просто убить все python процессы
taskkill /F /IM python.exe >nul 2>&1

echo.
echo [OK] Бот остановлен
echo.

pause
