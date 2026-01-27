import telebot
from telebot import types
from datetime import datetime, time
from dotenv import load_dotenv
import os
from pathlib import Path

# Загружаем переменные из .env рядом с bot.py
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError(f"Не задан TELEGRAM_BOT_TOKEN в .env по пути {env_path}")

bot = telebot.TeleBot(BOT_TOKEN)

# Ночной интервал для NightGuard
NIGHT_START = time(22, 0)
NIGHT_END = time(9, 0)


def is_night() -> bool:
    """Проверка: сейчас ночь или нет."""
    now = datetime.now().time()
    return NIGHT_START <= now or now <= NIGHT_END


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('/track', '/templates', '/night', '/pay')
    bot.send_message(
        message.chat.id,
        (
            '🔥 TrackOrderPro WB/Ozon\n'
            '/track 123456 → статус заказа\n'
            '/templates → шаблоны ответов\n'
            '/night → ночной режим\n'
            '/pay → 300₽/мес'
        ),
        reply_markup=markup
    )


@bot.message_handler(commands=['track'])
def track(message):
    # Пока заглушка без WB API
    bot.reply_to(
        message,
        '📦 /track 123456789\n'
        '(MVP: пока без WB API, D3 подключим реальные статусы)'
    )


@bot.message_handler(commands=['templates'])
def templates(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(
        'Размер M 42-44 (2-3д WB)', callback_data='size'
    )
    btn2 = types.InlineKeyboardButton(
        'Возврат FBO 3-5д', callback_data='return'
    )
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, '💬 Шаблоны WB:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == 'size':
        bot.send_message(
            call.message.chat.id,
            '👕 M 42-44. Отправка 2-3 дня WB!'
        )
    elif call.data == 'return':
        bot.send_message(
            call.message.chat.id,
            '🔄 Возврат FBO: фото + чат WB.'
        )


@bot.message_handler(commands=['night'])
def night(message):
    if is_night():
        bot.reply_to(
            message,
            '🌙 Ночь! Авто-ответ: "900 MSK, статус утром"'
        )
    else:
        bot.reply_to(
            message,
            '☀️ Сейчас день. Используй /track!'
        )


@bot.message_handler(commands=['pay'])
def pay(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(
        '300₽ QR YooKassa',
        url='https://yoomoney.ru/to41001750951472'  # твоя касса
    )
    markup.add(btn)
    bot.send_message(
        message.chat.id,
        '💳 300₽/мес TrackOrderPro',
        reply_markup=markup
    )


if __name__ == "__main__":
    print("Бот запущен (MVP без WB API).")
    bot.infinity_polling()
