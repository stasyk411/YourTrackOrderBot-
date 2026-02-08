"""
handlers/templates.py - Обработчики для работы с шаблонами ответов
"""

from telebot import types

def handle_templates(bot, message, TEMPLATES_DATABASE):
    """
    Обработчик команды /templates
    
    Args:
        bot: Экземпляр telebot.TeleBot
        message: Объект сообщения
        TEMPLATES_DATABASE: Словарь с шаблонами
    """
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("📏 Размеры", callback_data="cat_size"))
    markup.add(types.InlineKeyboardButton("🚚 Доставка", callback_data="cat_delivery"))
    markup.add(types.InlineKeyboardButton("🏪 ПВЗ", callback_data="cat_pvz"))
    markup.add(types.InlineKeyboardButton("🔄 Возврат", callback_data="cat_return"))
    markup.add(types.InlineKeyboardButton("💰 Цена", callback_data="cat_price"))
    markup.add(types.InlineKeyboardButton("😍 Эмоции", callback_data="cat_emotion"))
    
    bot.send_message(
        message.chat.id,
        "📝 *Шаблоны ответов (6 категорий, 30+ шаблонов):*",
        reply_markup=markup,
        parse_mode="Markdown"
    )

def handle_templates_callback(bot, call, TEMPLATES_DATABASE):
    """
    Обработчик выбора категории и навигации по страницам шаблонов.
    
    Args:
        bot: Экземпляр telebot.TeleBot
        call: Объект callback-запроса
        TEMPLATES_DATABASE: Словарь с шаблонами
    """
    
    # Определяем, что нажали: категорию или страницу
    if call.data.startswith('cat_'):
        # Нажали категорию — показываем первую страницу
        category = call.data  # например, 'cat_size'
        page = 0
    elif call.data.startswith('page_'):
        # Нажали страницу — парсим данные
        # Формат: page_cat-size_1 (категория_страница)
        _, category, page_str = call.data.split('_', 2)
        category = f"cat_{category}"
        page = int(page_str)
    elif call.data == "back_to_categories":
        # Возвращаем к выбору категорий
        handle_templates(bot, call.message, TEMPLATES_DATABASE)
        bot.answer_callback_query(call.id)
        return
    else:
        bot.answer_callback_query(call.id, "❌ Неизвестный запрос")
        return
    
    # Получаем шаблоны для категории
    templates = TEMPLATES_DATABASE.get(category, ["📝 Шаблон готов!"])
    total_pages = len(templates)
    
    # Если страница вне диапазона
    if page >= total_pages:
        page = 0
    
    # Отправляем текущий шаблон
    current_template = templates[page]
    page_display = f"📄 {page + 1}/{total_pages}"
    
    # Создаём навигационные кнопки
    markup = types.InlineKeyboardMarkup(row_width=3)
    
    # Кнопка "Предыдущая"
    if page > 0:
        prev_page = page - 1
        cat_key = category.replace('cat_', '')  # Убираем 'cat_' для callback
        markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{cat_key}_{prev_page}"))
    
    # Кнопка "Следующая"
    if page < total_pages - 1:
        next_page = page + 1
        cat_key = category.replace('cat_', '')
        # Если уже есть кнопка "Назад", добавляем в тот же ряд
        if page > 0:
            markup.add(types.InlineKeyboardButton("Далее ➡️", callback_data=f"page_{cat_key}_{next_page}"))
        else:
            markup.add(types.InlineKeyboardButton("Далее ➡️", callback_data=f"page_{cat_key}_{next_page}"))
    
    # Кнопка "Выбрать другой раздел"
    markup.add(types.InlineKeyboardButton("📂 Другие разделы", callback_data="back_to_categories"))
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"{current_template}\n\n{page_display}",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id)

def handle_quick_template_callback(bot, call):
    """
    Обработчик кнопки 'Ответить шаблоном' из парсинга
    
    Args:
        bot: Экземпляр telebot.TeleBot
        call: Объект callback-запроса
    """
    bot.answer_callback_query(call.id, "📝 Открываю шаблоны...")
    
    # Импортируем TEMPLATES_DATABASE
    from data.templates_database import TEMPLATES_DATABASE
    
    # Открываем меню шаблонов
    handle_templates(bot, call.message, TEMPLATES_DATABASE)