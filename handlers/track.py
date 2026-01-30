# handlers/track.py
import random
from telebot import types

TRACK_STATUSES = ["📦 Собран", "🚚 В пути", "✅ Доставлен", "❌ Отменён"]


def register_handlers_track(bot):
    @bot.message_handler(commands=['track'])
    def track(message):
        parts = message.text.split(maxsplit=1)
        if len(parts) == 1:
            bot.reply_to(
                message,
                "Введите номер заказа: /track 123456789"
            )
            return

        order_id = parts[1].strip()
        if not (order_id.isdigit() and len(order_id) in (8, 9)):
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(
                    "📋 Пример трека",
                    callback_data="track_example"
                )
            )
            bot.reply_to(
                message,
                "❌ Неверный трек: используй 8–9 цифр (пример: 12345678)",
                reply_markup=markup
            )
            return

        status = random.choice(TRACK_STATUSES)
        bot.reply_to(message, f"📦 #{order_id}\n{status}")
