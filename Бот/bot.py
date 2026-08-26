import os
import logging
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Поддерживаемые платформы
SUPPORTED_PLATFORMS = [
    'tiktok.com',
    'vt.tiktok.com',
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
    """Проверяет, содержит ли текст ссылку на поддерживаемый сервис"""
    return any(platform in text.lower() for platform in SUPPORTED_PLATFORMS)

async def download_tiktok_api(url: str, save_path: str) -> str:
    """Скачивание TikTok через прямое API (работает стабильно без вылетов yt-dlp)"""
    api_url = "https://www.tikwm.com/api/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, data={'url': url}, headers=headers) as resp:
            data = await resp.json()
            if data.get('code') != 0:
                raise Exception("Не удалось получить видео из TikTok. Ссылка приватная или недоступна.")
            
            video_url = data['data']['play']  # Видео без водяного знака
            title = data['data'].get('title', 'TikTok video')
            
            async with session.get(video_url) as video_resp:
                if video_resp.status == 200:
                    with open(save_path, 'wb') as f:
                        f.write(await video_resp.read())
                    return title
                raise Exception(f"Ошибка при скачивании файла: статус {video_resp.status}")

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
        return

    status_message = await update.message.reply_text("⏳ Скачиваю видео...")

    os.makedirs('downloads', exist_ok=True)
    video_path = f"downloads/{update.message.message_id}.mp4"
    video_title = "Video"

    try:
        # Проверяем, относится ли ссылка к TikTok (включая vt.tiktok.com)
        if 'tiktok.com' in url.lower():
            video_title = await download_tiktok_api(url, video_path)
        else:
            # Для остальных соцсетей используем yt-dlp
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': video_path,
                'quiet': True,
                'no_warnings': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_title = info.get('title', 'video')

        # Проверка размера файла (лимит Telegram 50 MB)
        file_size = os.path.getsize(video_path)
        max_size = 50 * 1024 * 1024

        if file_size > max_size:
            await status_message.edit_text(
                "❌ Видео слишком большое (>50 MB). Telegram не позволяет отправить такой файл."
            )
            return

        await status_message.edit_text("📤 Отправляю видео...")

        with open(video_path, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption=f"📹 {video_title[:100]}",
                supports_streaming=True
            )

        await status_message.delete()

    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        await status_message.edit_text(
            f"❌ Ошибка при скачивании видео:\n{str(e)[:200]}"
        )
    finally:
        # Всегда удаляем скачанный файл после работы
        if os.path.exists(video_path):
            os.remove(video_path)

async def request_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Прослушиватель всех входящих сообщений"""
    if update.message:
        user = update.message.from_user
        chat = update.message.chat
        text = update.message.text or "[no text]"

        logger.info(f"📨 Incoming request:")
        logger.info(f"   User: {user.first_name} (@{user.username}) [ID: {user.id}]")
        logger.info(f"   Chat: {chat.type} [ID: {chat.id}]")
        logger.info(f"   Message: {text[:100]}")

        await handle_request(update, context)

async def handle_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Центральный обработчик всех запросов"""
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    if text.startswith('/'):
        return

    if is_video_link(text):
        await download_and_send_video(update, context)
    else:
        logger.info(f"   ⚠️ Not a video link, ignoring")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок приложения"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Запуск бота"""
    # Вставляем токен напрямую в переменную без os.getenv
    token = '8648442240:AAEuVV8HoSGYqwOvqusam_Ce1uBrg_ERXpk'

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, request_listener))
    application.add_error_handler(error_handler)

    print("[OK] Bot started successfully!")
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    if not token:
        print("❌ Ошибка: Установите переменную окружения TELEGRAM_BOT_TOKEN")
        print("Пример (Linux/macOS): export TELEGRAM_BOT_TOKEN='ваш_токен'")
        print("Пример (Windows CMD): set TELEGRAM_BOT_TOKEN=ваш_токен")
        return

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, request_listener))
    application.add_error_handler(error_handler)

    print("[OK] Bot started successfully!")
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()