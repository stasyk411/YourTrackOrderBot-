from telebot import types


def register_handlers_templates(bot):
    """Умение бота: команда /templates с кнопками размеров."""

    @bot.message_handler(commands=['templates'])
    def templates(message):
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("М 42-44, рост 172-178", callback_data="size_m")
        btn2 = types.InlineKeyboardButton("FBO 3-5 дней", callback_data="fbo_time")
        markup.add(btn1, btn2)

        bot.send_message(
            message.chat.id,
            "Выбери вариант ответа для клиента WB:",
            reply_markup=markup,
        )

    @bot.callback_query_handler(func=lambda call: call.data in ["size_m", "fbo_time"])
    def callback_templates(call):
        if call.data == "size_m":
            bot.send_message(
                call.message.chat.id,
                "По размеру: обычно подойдёт М (42–44), на рост 172–178 см.",
            )
        elif call.data == "fbo_time":
            bot.send_message(
                call.message.chat.id,
                "По срокам: обычно FBO-отправка до ПВЗ занимает 3–5 дней.",
            )
