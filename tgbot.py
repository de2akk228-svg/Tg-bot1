import asyncio
import os

import pip 
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
# Получаем переменные из окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN не установлен. Установите переменную окружения.")

bot = Bot(token=TOKEN)
dp = Dispatcher()
links = {}

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("✉️ Напиши сообщение или пришли фото — я передам анонимно.")

@dp.message()
async def handler(message: types.Message):
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
                f"💬 Сообщение:\n\n{message.text}"
            )
        links[sent.message_id] = message.from_user.id
        await message.answer("✅ Отправлено.")
        return

    if message.reply_to_message:
        mid = message.reply_to_message.message_id
        if mid in links:
            uid = links[mid]
            if message.photo:
                await bot.send_photo(uid, message.photo[-1].file_id, caption=message.caption or "")
            else:
                await bot.send_message(uid, message.text)
            await message.answer("📨 Ответ отправлен.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
