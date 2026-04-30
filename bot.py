import asyncio
import time
import re
import random
from collections import defaultdict

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramForbiddenError

BOT_TOKEN = "8457589172:AAFBsnyBVIcyn5Oi6XkJqsBtQaYslMTS6so"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 🔴 антиспам
user_messages = defaultdict(list)
SPAM_LIMIT = 5
SPAM_TIME = 10

# 🔴 счетчик мата
user_bad_words = defaultdict(int)
BAD_WORDS_WARNING = 3

# 🔴 мат (с учетом обходов)
BAD_PATTERNS = [
    r"бл[\w*#@!]*", r"х[\w*#@!]*й", r"п[\w*#@!]*зда",
    r"е[\w*#@!]*б", r"с[\w*#@!]*ка", r"долбо[\w*#@!]*",
    r"муд[\w*#@!]*", r"ганд[\w*#@!]*", r"пид[\w*#@!]*"
]

# 🧠 нормализация текста
def normalize(text):
    text = text.lower()
    text = text.replace("ё", "е")
    text = re.sub(r"[^a-zа-я0-9\s]", " ", text)
    return text

# 🟢 ответы (вариативные)
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

# 🧠 логика определения смысла
def detect_intent(text):
    words = text.split()

    # Далат
    if "далат" in words:
        return "manager"

    # морская прогулка
    if "морск" in text or "яхт" in text or "катер" in text:
        return "manager"

    # бронирование
    if any(w in text for w in ["заброн", "брони", "запис"]):
        return "manager"

    # цены
    if any(w in text for w in ["сколько", "цена", "стоим"]):
        return "manager"

    # аренда байка
    if any(w in text for w in ["байк", "скутер", "прокат", "аренд", "оренд"]):
        return "bike"

    # обмен валют
    if any(w in text for w in ["обмен", "валют", "донг"]):
        return "exchange"

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

    # 🔴 мат
    if contains_bad_word(text):
        user_bad_words[user_id] += 1
        await message.delete()

        if user_bad_words[user_id] == BAD_WORDS_WARNING:
            await message.answer("⚠️ Пожалуйста, соблюдайте правила общения")
        elif user_bad_words[user_id] > BAD_WORDS_WARNING:
            try:
                await message.chat.kick(user_id)
                await message.answer("🚫 Пользователь удалён за нарушения")
            except TelegramForbiddenError:
                pass
        return

    # 🔴 блок Trip.com
    if "trip.com" in text:
        await message.delete()
        return

    # 🧠 определение намерения
    intent = detect_intent(text)

    if intent:
        reply = random.choice(ANSWERS[intent])
        await message.answer(reply)
        return

    # ❗ иначе молчит

async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
