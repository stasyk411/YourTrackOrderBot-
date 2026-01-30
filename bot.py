import telebot
from datetime import datetime
from core.config import get_bot_config
from handlers.start import register_handlers_start
from handlers.track import register_handlers_track
from handlers.templates import register_handlers_templates
from handlers.night import register_handlers_night


config = get_bot_config()
bot = telebot.TeleBot(config.token)


def is_night() -> bool:
    """Проверка: сейчас ночь или нет."""
    now = datetime.now().time()
    return config.night_start <= now or now <= config.night_end


# Регистрируем хендлеры из модулей
register_handlers_start(bot)
register_handlers_track(bot)
register_handlers_templates(bot)
register_handlers_night(bot)


if __name__ == "__main__":
    print("Бот запущен (MVP без WB API).")
    bot.infinity_polling()
