@echo off
echo ====================================
echo   Telegram Video Downloader Bot
echo ====================================
echo.

REM Проверяем наличие токена
if "%TELEGRAM_BOT_TOKEN%"=="" (
    echo [ОШИБКА] Токен не установлен!
    echo.
    echo Установите токен одним из способов:
    echo 1. Через PowerShell:
    echo    $env:TELEGRAM_BOT_TOKEN = "your_token_here"
    echo.
    echo 2. Или введите токен сейчас:
    set /p TELEGRAM_BOT_TOKEN="Введите токен бота: "
    if "%TELEGRAM_BOT_TOKEN%"=="" (
        echo Токен не введен. Выход.
        pause
        exit /b 1
    )
)

echo [OK] Токен найден
echo [INFO] Запуск бота...
echo.

python bot.py

pause
