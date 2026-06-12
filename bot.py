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
        # В групповых чатах не отвечаем на не-ссылки
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

async def request_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Прослушиватель всех входящих запросов"""
    if update.message:
        user = update.message.from_user
        chat = update.message.chat
        text = update.message.text or "[no text]"

        # Логируем информацию о запросе
        logger.info(f"📨 Incoming request:")
        logger.info(f"   User: {user.first_name} (@{user.username}) [ID: {user.id}]")
        logger.info(f"   Chat: {chat.type} [ID: {chat.id}]")
        logger.info(f"   Message: {text[:100]}")

        # Здесь можно добавить дополнительную логику:
        # - Сохранение статистики
        # - Проверка бан-листа
        # - Анти-спам фильтры
        # - Аналитика использования

        # Передаем управление дальше в handle_request
        await handle_request(update, context)

async def handle_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Центральный обработчик всех запросов"""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    # Проверяем, является ли это командой
    if text.startswith('/'):
        # Команды обрабатываются отдельными хендлерами
        return

    # Проверяем, является ли это ссылкой на видео
    if is_video_link(text):
        await download_and_send_video(update, context)
    else:
        # Необязательно: отвечаем на текст без ссылки
        logger.info(f"   ⚠️ Not a video link, ignoring")

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
    # Прослушиватель для всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, request_listener))
    application.add_error_handler(error_handler)

    # Запускаем бота
    print("[OK] Bot started successfully!")
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
