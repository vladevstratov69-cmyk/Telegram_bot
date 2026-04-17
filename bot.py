import asyncio
import time
from collections import defaultdict

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart

# 🔑 ВСТАВЬ СЮДА ТОКЕН БОТА
BOT_TOKEN = "8457589172:AAFBsnyBVIcyn5Oi6XkJqsBtQaYslMTS6so"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 🔴 запрещённые слова (можешь дополнять)
BAD_WORDS = [
    "бля", "блять", "сука", "хер", "хуй", "пизда",
    "ебать", "ебаный", "нахуй", "долбоеб", "мудак",
    "гандон", "пидор", "пидорас"
]

# 🟢 ответы на вопросы (бот реагирует ТОЛЬКО на эти ключевые слова)
FAQ = {
    "как забронировать": "✈️ Чтобы забронировать экскурсию, напишите менеджеру: @red_star_Manager",
    "как забронировать экскурсию": "✈️ Напишите менеджеру: @red_star_Manager",
}

# 🔴 антиспам
user_messages = defaultdict(list)
SPAM_LIMIT = 5  # сообщений
SPAM_TIME = 10  # секунд

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("👋 Привет! Я бот этого чата. Отвечаю только на вопросы и слежу за порядком 🤖")

async def check_spam(message: Message):
    user_id = message.from_user.id
    now = time.time()

    user_messages[user_id] = [
        t for t in user_messages[user_id] if now - t < SPAM_TIME
    ]
    user_messages[user_id].append(now)

    if len(user_messages[user_id]) > SPAM_LIMIT:
        await message.delete()
        return True

    return False

@dp.message()
async def handle_message(message: Message):
    if not message.text:
        return

    text = message.text.lower()

    # 🔴 антиспам (без банов)
    if await check_spam(message):
        return

    # 🔴 мат
    for word in BAD_WORDS:
        if word in text:
            await message.delete()
            return

    # 🔴 блокировка ссылок на Trip.com
    if "http" in text or "t.me" in text:
        if "trip.com" in text:
            await message.delete()
            return

    # 🟢 ответ только по ключевым словам
    for key, answer in FAQ.items():
        if key in text:
            await message.answer(answer)
            return

    # ❗ в остальных случаях бот молчит

async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())