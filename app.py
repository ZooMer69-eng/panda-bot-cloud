import asyncio
import logging
import aiohttp
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import PreCheckoutQuery, Message, WebAppInfo, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = "9244645218:AAFopJ-hOND0D5dQx9qzZurAUTbAWQpKs3A"
WEBAPP_URL = "https://panda-server-wuhd.onrender.com"
API_URL = "https://panda-server-wuhd.onrender.com"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🎮 Играть", web_app=WebAppInfo(url=WEBAPP_URL)))
    await message.answer(
        "Привет! Добро пожаловать в Panda Game! 🐼\nНажми кнопку ниже, чтобы начать играть.",
        reply_markup=builder.as_markup()
    )

@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    print("DEBUG: Подтверждаем платеж...")
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def process_successful_payment(message: Message):
    print("DEBUG: Платеж прошел! Начисляем гемы...")
    payload = message.successful_payment.invoice_payload
    parts = payload.split("_")
    gems = int(parts[1])
    user_id = str(message.from_user.id)
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/api/add_gems", json={"user_id": user_id, "amount": gems}) as resp:
            if resp.status == 200:
                await message.answer(f"✅ Успешно! Тебе начислено {gems} гемов 💎. Зайди в игру и проверь профиль!")
            else:
                await message.answer("❌ Ошибка при начислении гемов. Попробуй позже.")

# --- ЗАГЛУШКА ДЛЯ KOYEB (чтобы сервис не засыпал и не выдавал ошибку) ---
async def health_check(request):
    return web.Response(text="Bot is alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Health check server started on port {port}")

async def main():
    print("Бот запущен и ждет сообщений!")
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
