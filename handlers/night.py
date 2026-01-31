from telebot import types
from datetime import datetime, time
from core.config import get_bot_config

def get_time_state(now: datetime) -> str:
    config = get_bot_config()
    now_msk = now.time()

    if now_msk >= config.night_start or now_msk <= config.night_end:
        return "🌙 Ночь (автоответ, не трекать)"
    elif config.morning_start <= now_msk < config.morning_end:
        return "🌅 Утро (можно трекать)"
    elif config.day_start <= now_msk < config.day_end:
        return "☀️ День (можно трекать)"
    elif config.evening_start <= now_msk < config.evening_end:
        return "🌆 Вечер (можно трекать)"
    return "☀️ День (можно трекать)"

def register_handlers_night(bot):  # ← bot передаётся параметром!
    @bot.message_handler(commands=['night'])
    def night_handler(message):
        now = datetime.now()
        state = get_time_state(now)
        bot.reply_to(message, f"⏰ Сейчас {state} (MSK)")
