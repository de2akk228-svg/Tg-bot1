import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
import threading

# ==================== FLASK ДЛЯ RAILWAY ====================



def home():
    return "🤖 Анонимный бот работает!"


def health():
    return "OK", 200

# ==================== TELEGRAM БОТ ====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not TOKEN:
    logger.error("❌ TELEGRAM_TOKEN не установлен!")
    raise ValueError("Установи TELEGRAM_TOKEN в Railway Variables")

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
links = {}

@dp.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer("✉️ Напиши сообщение или пришли фото — я передам анонимно.")

@dp.message()
async def handle_message(message: types.Message):
    try:
        # Сообщение ОТ пользователя К админу
        if message.from_user.id != ADMIN_ID:
            if message.photo:
                sent = await bot.send_photo(
                    ADMIN_ID,
                    message.photo[-1].file_id,
                    caption="📸 Фото от анонима"
                )
            else:
                sent = await bot.send_message(
                    ADMIN_ID,
                    f"💬 Сообщение от анонима:\n\n{message.text}"
                )
            # Сохраняем связь для ответа
            links[sent.message_id] = message.from_user.id
            await message.answer("✅ Отправлено анонимно.")
            return
        
        # Сообщение ОТ админа (ответ)
        if message.reply_to_message:
            mid = message.reply_to_message.message_id
            if mid in links:
                uid = links[mid]  # ID пользователя
                if message.photo:
                    await bot.send_photo(
                        uid,
                        message.photo[-1].file_id,
                        caption=message.caption or "📸 Ответ с фото"
                    )
                else:
                    await bot.send_message(uid, f"📨 Ответ от админа:\n\n{message.text}")
                await message.answer("✅ Ответ отправлен.")
                
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await message.answer("❌ Произошла ошибка.")

async def start_telegram_bot():
    """Запускаем Telegram бота"""
    logger.info("🚀 Запускаю Telegram бота...")
    await dp.start_polling(bot)

def run_bot():
    """Запуск в отдельном потоке"""
    asyncio.run(start_telegram_bot())

# ==================== ЗАПУСК ====================
if __name__ == '__main__':
    # Запускаем Telegram бота в фоне
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask сервер (для Railway)
    port = int(os.environ.get("PORT", 3000))
    logger.info(f"🌐 Веб-сервер запущен на порту {port}")
  