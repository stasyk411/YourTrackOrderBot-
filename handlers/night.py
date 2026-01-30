from telebot import types
from core.config import NIGHT_START, NIGHT_END
from datetime import datetime, time

def get_time_state(now: time) -> str:
    """Возвращает состояние времени суток по MSK стандартам."""
    if now <= time(6, 0):           # 00:00–06:00
        return "🌙 Ночь (не отвечай клиентам!)"
    elif now < time(12, 0):         # 06:00–12:00
        return "☀️ Утро (можно трекать)"
    elif now < time(18, 0):         # 12:00–18:00
        return "🌤️ День (можно трекать)"
    elif now < NIGHT_START:         # 18:00–22:00
        return "🌆 Вечер (можно трекать)"
    else:                           # 22:00–00:00
        return "🌙 Ночь (не отвечай клиентам!)"

def register_handlers_night(bot):
    """Команда /night показывает текущее время суток."""
    
    @bot.message_handler(commands=['night'])
    def night(message):
        now = datetime.now().time()
        state = get_time_state(now)
        bot.reply_to(message, f"⏰ Сейчас {state} (MSK)")
