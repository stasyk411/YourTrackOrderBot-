import telebot
from core.config import get_config

config = get_config()
bot = telebot.TeleBot(config.token)

# Сбрасываем offset (последнее обработанное сообщение)
bot.skip_updates()  
print("Offset сброшен. Теперь можно запускать бота.")
