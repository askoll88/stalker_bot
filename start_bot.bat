@echo off
chcp 65001 >nul
title S.T.A.L.K.E.R. Bot

echo ========================================
echo   S.T.A.L.K.E.R. Bot - ЗАПУСК
echo ========================================
echo.

cd /d "%~dp0"

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python не найден!
    echo Установите Python: https://python.org
    pause
    exit /b 1
)

echo [OK] Python найден
echo.

REM Проверка зависимостей
echo [INFO] Проверка зависимостей...
pip show vk-api >nul 2>&1
if errorlevel 1 (
    echo [INFO] Установка зависимостей...
    pip install -r requirements.txt
)

echo.
echo ========================================
echo   ЗАПУСК БОТА...
echo ========================================
echo.

REM Создаем папку для логов
if not exist "logs" mkdir logs

REM Запуск бота в новом окне с логами
start "S.T.A.L.K.E.R. Bot - Лог" /d "%~dp0" cmd /c "python main.py 2^>^&1 | tee logs\bot.log & pause"

echo [OK] Бот запущен в новом окне
echo Логи сохраняются в: logs\bot.log
echo.
echo Для остановки бота запустите stop_bot.bat
echo.

pause
