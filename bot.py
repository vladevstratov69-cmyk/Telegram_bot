import asyncio
import time
from collections import defaultdict

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramForbiddenError

# 🔑 ВСТАВЬ СЮДА ТОКЕН БОТА
BOT_TOKEN = "8457589172:AAFBsnyBVIcyn5Oi6XkJqsBtQaYslMTS6so"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 🔴 запрещённые слова
BAD_WORDS = [
    "бля", "блять", "сука", "хер", "хуй", "пизда",
    "ебать", "ебаный", "нахуй", "долбоеб", "мудак",
    "гандон", "пидор", "пидорас"
]

FAQ = {
    "как забронировать": "✈️ Чтобы забронировать экскурсию, напишите менеджеру: @red_star_Manager",
    "как забронировать экскурсию": "✈️ Напишите менеджеру: @red_star_Manager",
}

user_messages = defaultdict(list)
user_bad_words = defaultdict(int)
SPAM_LIMIT = 5
SPAM_TIME = 10
BAD_WORDS_WARNING = 3

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("👋 Привет! Я бот этого чата. Отвечаю только на вопросы и слежу за порядком 🤖")

async def check_spam(message: Message):
    user_id = message.from_user.id
    now = time.time()

    user_messages[user_id] = [t for t in user_messages[user_id] if now - t < SPAM_TIME]
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
    user_id = message.from_user.id

    if await check_spam(message):
        return

    # 🔴 удаляем любые ссылки
    if "http://" in text or "https://" in text or "t.me" in text or ".com" in text or ".ru" in text:
        await message.delete()
        return

    # 🔴 обработка матов
    if any(word in text for word in BAD_WORDS):
        user_bad_words[user_id] += 1
        await message.delete()

        if user_bad_words[user_id] == BAD_WORDS_WARNING:
            await message.answer(
                f"⚠️ Вы использовали запрещённые слова {BAD_WORDS_WARNING} раза. Ещё одно подобное сообщение — и вы будете заблокированы."
            )
            return
        elif user_bad_words[user_id] > BAD_WORDS_WARNING:
            try:
                await message.chat.kick(user_id)
                await message.answer(
                    "🚫 Пользователь был заблокирован за повторное употребление мата."
                )
            except TelegramForbiddenError:
                await message.answer(
                    "❗ Я не могу заблокировать пользователя, так как у меня нет на это прав администратора."
                )
            return
        return

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
