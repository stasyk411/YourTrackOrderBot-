from telebot import types


def register_handlers_start(bot):
    """Регистрация хендлера для /start."""

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
