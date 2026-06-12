import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import re

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Поддерживаемые платформы
SUPPORTED_PLATFORMS = [
    'tiktok.com',
    'instagram.com',
    'youtube.com',
    'youtu.be',
    'twitter.com',
    'x.com',
    'facebook.com',
    'reddit.com',
    'vimeo.com'
]

def is_video_link(text: str) -> bool:
    """Проверяет, содержит ли текст ссылку на видео"""
    return any(platform in text.lower() for platform in SUPPORTED_PLATFORMS)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "👋 Привет! Отправь мне ссылку на видео из:\n"
        "• TikTok\n"
        "• Instagram\n"
        "• YouTube\n"
        "• Twitter/X\n"
        "• Facebook\n"
        "• Reddit\n"
        "• Vimeo\n\n"
        "Я скачаю и отправлю тебе видео!"
    )

async def download_and_send_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Скачивает видео и отправляет в чат"""
    url = update.message.text.strip()

    if not is_video_link(url):
        await update.message.reply_text("❌ Это не похоже на поддерживаемую ссылку на видео.")
        return

    # Отправляем сообщение о начале скачивания
    status_message = await update.message.reply_text("⏳ Скачиваю видео...")

    try:
        # Настройки для yt-dlp
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # Создаем папку для скачивания
        os.makedirs('downloads', exist_ok=True)

        # Скачиваем видео
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            video_title = info.get('title', 'video')

        # Проверяем размер файла
        file_size = os.path.getsize(video_path)
        max_size = 50 * 1024 * 1024  # 50 MB лимит Telegram

        if file_size > max_size:
            await status_message.edit_text(
                "❌ Видео слишком большое (>50 MB). Telegram не позволяет отправить такой файл."
            )
            os.remove(video_path)
            return

        # Отправляем видео
        await status_message.edit_text("📤 Отправляю видео...")

        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption=f"📹 {video_title[:100]}",
                supports_streaming=True
            )

        # Удаляем статусное сообщение и файл
        await status_message.delete()
        os.remove(video_path)

    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        await status_message.edit_text(
            f"❌ Ошибка при скачивании видео:\n{str(e)[:200]}"
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Запуск бота"""
    # Получаем токен из переменной окружения
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not token:
        print("❌ Ошибка: Установите переменную окружения TELEGRAM_BOT_TOKEN")
        print("Пример: export TELEGRAM_BOT_TOKEN='your_token_here'")
        return

    # Создаем приложение
    application = Application.builder().token(token).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_and_send_video))
    application.add_error_handler(error_handler)

    # Запускаем бота
    print("🤖 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
