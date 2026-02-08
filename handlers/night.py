"""
handlers/night.py - Обработчик команды /night
Показывает текущее время и режим работы (ночной/дневной)
"""

from datetime import datetime

def get_time_state(now: datetime, config) -> str:
    """
    Определяет временной период (ночь/утро/день/вечер)
    
    Args:
        now: Текущее время datetime
        config: Конфигурация из core.config.Config
        
    Returns:
        str: Описание периода
    """
    now_msk = now.time()

    if now_msk >= config.night_start or now_msk <= config.night_end:
        return "🌙 Ночь (автоответ)"
    elif config.morning_start <= now_msk < config.morning_end:
        return "🌅 Утро (трекать)"
    elif config.day_start <= now_msk < config.day_end:
        return "☀️ День (трекать)"
    elif config.evening_start <= now_msk < config.evening_end:
        return "🌆 Вечер (трекать)"
    return "☀️ День (трекать)"


def handle_night(bot, message, config):
    """
    Обработчик команды /night
    
    Args:
        bot: Экземпляр telebot.TeleBot
        message: Объект сообщения
        config: Конфигурация из core.config.Config
    """
    now = datetime.now()
    state = get_time_state(now, config)
    bot.reply_to(message, f"⏰ Сейчас: {state} (MSK)")


def register(bot, config):
    """
    Регистрирует хендлеры для команды /night
    
    Args:
        bot: Экземпляр telebot.TeleBot
        config: Конфигурация из core.config.Config
    """
    @bot.message_handler(commands=['night', 'ночь'])
    def night_wrapper(message):
        """Обёртка для регистрации в декораторе"""
        handle_night(bot, message, config)
    
    print("✅ Хендлер /night зарегистрирован")