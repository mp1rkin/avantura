# avantura
we s moim drunom KOZLOVIM NIKITOI v etom repozirtorii delam dengi i pizdec

---

## Telegram Video Downloader Bot

Бот для Telegram, который скачивает видео из TikTok, Instagram, YouTube и других платформ.

### Поддерживаемые платформы

- TikTok
- Instagram
- YouTube
- Twitter/X
- Facebook
- Reddit
- Vimeo

### Установка

1. Установите Python 3.8+

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте бота через [@BotFather](https://t.me/botfather) в Telegram:
   - Отправьте `/newbot`
   - Выберите имя и username для бота
   - Скопируйте токен

4. Установите токен в переменную окружения:

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_BOT_TOKEN = "your_token_here"
```

**Linux/Mac:**
```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
```

### Запуск

```bash
python bot.py
```

### Использование

1. Найдите вашего бота в Telegram
2. Отправьте `/start`
3. Отправьте ссылку на видео
4. Бот скачает и отправит видео

### Ограничения

- Максимальный размер видео: 50 MB (лимит Telegram)
- Для больших видео рекомендуется использовать Telegram Bot API с file_id

### Примечания

- Бот использует `yt-dlp` для скачивания видео
- Скачанные файлы автоматически удаляются после отправки
- Логи сохраняются в консоли
