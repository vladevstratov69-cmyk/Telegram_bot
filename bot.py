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

# 🔴 расширенный список запрещённых слов и производных
BAD_WORDS = [
    "бля", "блять", "ебать", "ебан", "еб", "ёб", "ёбан", "заеб", "заёб",
    "хер", "херня", "ху", "хуй", "хуя", "оху", "поху", "ниху", "пизд", "пизда", "пиздец",
    "сука", "сучк", "сук", "гандон", "мудак", "мудила", "долбоёб", "долбаёб", "долбоеб",
    "пидарас", "пидор", "педик", "мразь", "чмо", "урод", "сволочь", "скотина", "шлюха",
    "тварь", "жопа", "жопой", "сукин", "суки", "уеб", "уёб", "выеб", "выёб",
    "обосрал", "обоссал", "дрянь", "говно", "дерьмо", "дроч", "дрочить", "срать", "ссы"
]

FAQ = {
    "как забронировать": "✈️ Чтобы забронировать экскурсию, напишите менеджеру: @red_star_Manager",
    "как забронировать экскурсию": "✈️ Напишите менеджеру: @red_star_Manager",

    # новые вопросы
    "к кому обратиться по обмену валют": "💱 Напишите, пожалуйста, нашим коллегам @RED_STAR_EXCHANGER.",
    "обмену валют": "💱 Напишите, пожалуйста, нашим коллегам @RED_STAR_EXCHANGER.",
    "где выгодно обменять рубли на донги": "💱 Напишите, пожалуйста, нашим коллегам @RED_STAR_EXCHANGER.",
    "где можно ознакомиться со всеми экскурсиями и ценами": "📌 В закрепе чата есть информация обо всех экскурсиях с ценами и подробным описанием.",
    "ознакомиться со всеми экскурсиями и ценами": "📌 В закрепе чата есть информация обо всех экскурсиях с ценами и подробным описанием.",
    "где экскурсии и цены": "📌 В закрепе чата есть информация обо всех экскурсиях с ценами и подробным описанием.",
    "экскурсии и цены": "📌 В закрепе чата есть информация обо всех экскурсиях с ценами и подробным описанием.",
}

user_messages = defaultdict(list)
user_bad_words = defaultdict(int)
SPAM_LIMIT = 5
SPAM_TIME = 10
BAD_WORDS_WARNING = 3

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("👋 Привет! Я бот этого чата. Отвечаю на популярные вопросы и слежу за порядком 🤖")

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

    # 🔴 обработка матов
    if any(bad in text for bad in BAD_WORDS):
        user_bad_words[user_id] += 1
        await message.delete()

        if user_bad_words[user_id] == BAD_WORDS_WARNING:
            await message.answer(
                f"⚠️ Вы использовали запрещённые слова 3 раза. Следующее нарушение — и вы будете исключены из чата."
            )
            return
        elif user_bad_words[user_id] > BAD_WORDS_WARNING:
            try:
                await message.chat.kick(user_id)
                await message.answer(
                    "🚫 Пользователь был исключён за повторное использование ненормативной лексики."
                )
            except TelegramForbiddenError:
                await message.answer(
                    "❗ Я не могу исключить пользователя, так как у меня нет на это прав администратора."
                )
            return
        return

    # 🟢 ответы на часто задаваемые вопросы (по ключам подстроки в тексте)
    for key, answer in FAQ.items():
        if key in text:
            await message.answer(answer)
            return

    # ❗ В остальных случаях бот молчит

async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
