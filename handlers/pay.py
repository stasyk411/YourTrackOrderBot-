"""
handlers/pay.py - Обработчик команды /pay
Монетизация и описание Pro-версии
"""

from telebot import types


def handle_pay(bot, message):
    """
    Обработчик команды /pay - показывает информацию о Pro-версии
    
    Args:
        bot: Экземпляр telebot.TeleBot
        message: Объект сообщения
    """
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(
        "💳 590₽ Pro (150+ шаблонов + NightGuard)", 
        url="https://yoomoney.ru/to/41001750951472"
    )
    markup.add(btn)
    
    pro_text = (
        "💰 *TrackOrderPro Pro - 590₽/месяц*\n\n"
        "• 150+ шаблонов с обновлениями\n"
        "• NightGuard (ночной автоответ)\n"
        "• Пакетная обработка отзывов\n"
        "• Приоритетная поддержка\n"
        "• Расширенная персонализация"
    )
    
    bot.send_message(
        message.chat.id, 
        pro_text, 
        reply_markup=markup,
        parse_mode="Markdown"
    )


def register(bot, config):
    """
    Регистрирует хендлеры для команды /pay
    
    Args:
        bot: Экземпляр telebot.TeleBot
        config: Конфигурация из core.config.Config
    """
    @bot.message_handler(commands=['pay', 'оплата'])
    def pay_wrapper(message):
        """Обёртка для регистрации в декораторе"""
        handle_pay(bot, message)
    
    print("✅ Хендлер /pay зарегистрирован")