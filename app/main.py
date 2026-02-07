"""
app/main.py - Основная инициализация бота
Здесь создается экземпляр бота и подключаются маршруты
"""

import telebot
from core.config import get_config

def create_bot():
    """Создает и возвращает экземпляр бота"""
    config = get_config()
    
    if not config.token:
        raise RuntimeError("ERROR: TELEGRAM_BOT_TOKEN missing in .env")
    
    bot = telebot.TeleBot(config.token)
    print("Bot initialized")
    return bot, config

def start_bot():
    """Запускает бота (основная функция)"""
    bot, config = create_bot()
    
    # Импортируем маршруты ДО запуска polling
    from app import routes
    routes.register_handlers(bot, config)
    
    print("TrackOrderPro started")
    print("Polling...")
    bot.infinity_polling()

if __name__ == "__main__":
    # Если запускаем этот файл напрямую
    start_bot()