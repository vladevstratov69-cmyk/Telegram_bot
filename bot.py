import asyncio
import time
import re
import random
from collections import defaultdict

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart

# 🔑 ВСТАВЬ НОВЫЙ ТОКЕН (старый обязательно отзови!)
BOT_TOKEN = "8457589172:AAHmeBb7qJF-Y2Am-z-vZwC8omDpacTyUcI"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 🔴 антиспам
user_messages = defaultdict(list)
SPAM_LIMIT = 5
SPAM_TIME = 10

# 🔴 счетчик мата
user_bad_words = defaultdict(int)
BAD_WORDS_WARNING = 3

# 🔴 мат (ловит обходы типа бл*ть, х#й и т.д.)
BAD_PATTERNS = [
    r"бл[\w]*", r"х[\w]*й", r"п[\w]*зда",
    r"е[\w]*б", r"с[\w]*ка", r"долбо[\w]*",
    r"муд[\w]*", r"ганд[\w]*", r"пид[\w]*"
]

# 🧠 нормализация текста
def normalize(text):
    text = text.lower()
    text = text.replace("ё", "е")
    text = re.sub(r"[^a-zа-я0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# 🟢 ответы
ANSWERS = {
    "manager": [
        "✈️ Напишите, пожалуйста, менеджеру: @red_star_Manager",
        "📩 Для записи напишите менеджеру: @red_star_Manager",
        "✈️ Менеджер всё подскажет: @red_star_Manager"
    ],
    "bike": [
        "🏍 Контакты есть в закрепе. Дублируем: @d1motors",
        "🏍 Напишите по аренде сюда: @d1motors",
        "🏍 По байкам пишите: @d1motors"
    ],
    "exchange": [
        "💱 Напишите нашим коллегам: @RED_STAR_EXCHANGER",
        "💱 По обмену валют сюда: @RED_STAR_EXCHANGER"
    ]
}

# 🧠 определение смысла
def detect_intent(text):
    # сначала байки (чтобы “сколько стоит байк” шло сюда)
    if any(w in text for w in ["байк", "скутер", "прокат", "аренд", "оренд"]):
        return "bike"

    # обмен валют
    if any(w in text for w in ["обмен", "валют", "донг"]):
        return "exchange"

    # Далат
    if "далат" in text:
        return "manager"

    # морская прогулка (уточнили)
    if "морск" in text and any(w in text for w in ["прогул", "тур", "экскурс"]):
        return "manager"

    # бронирование
    if any(w in text for w in ["заброн", "брони", "запис"]):
        return "manager"

    # цены
    if any(w in text for w in ["сколько", "цена", "стоим"]):
        return "manager"

    return None

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("👋 Привет! Я бот чата. Отвечаю на вопросы и слежу за порядком 🤖")

async def check_spam(message: Message):
    user_id = message.from_user.id
    now = time.time()

    user_messages[user_id] = [t for t in user_messages[user_id] if now - t < SPAM_TIME]
    user_messages[user_id].append(now)

    if len(user_messages[user_id]) > SPAM_LIMIT:
        await message.delete()
        return True
    return False

def contains_bad_word(text):
    return any(re.search(pattern, text) for pattern in BAD_PATTERNS)

@dp.message()
async def handle_message(message: Message):
    if not message.text:
        return

    text_raw = message.text
    text = normalize(text_raw)
    user_id = message.from_user.id

    # 🔴 антиспам
    if await check_spam(message):
        return

    # 🔴 мат (без киков, только предупреждение)
    if contains_bad_word(text):
        user_bad_words[user_id] += 1
        await message.delete()

        if user_bad_words[user_id] == BAD_WORDS_WARNING:
            await message.answer("⚠️ Пожалуйста, соблюдайте правила общения")
        return

    # 🔴 блок Trip.com (с учетом нормализации)
    if "trip com" in text or "trip.com" in text:
        await message.delete()
        return

    # 🧠 логика
    intent = detect_intent(text)

    if intent:
        reply = random.choice(ANSWERS[intent])
        await message.answer(reply)
        return

    # ❗ иначе бот молчит

async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
