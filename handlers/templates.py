"""
handlers/templates.py - Обработчик команды /templates
Показывает шаблоны ответов с использованием TemplateService
"""

import logging
from telebot import types

logger = logging.getLogger(__name__)


def handle_templates(bot, message, template_service, page: int = 0, items_per_page: int = 5):
    """
    Обработчик команды /templates - показывает шаблоны ответов
    
    Args:
        bot: Экземпляр telebot.TeleBot
        message: Объект сообщения
        template_service: Экземпляр TemplateService
        page: Номер страницы (для пагинации)
        items_per_page: Шаблонов на странице
    """
    try:
        # Получаем популярные шаблоны для текущей страницы
        all_popular = template_service.get_popular_templates(limit=50)
        
        # Пагинация
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        current_page_templates = all_popular[start_idx:end_idx]
        
        if not current_page_templates:
            bot.reply_to(message, "📭 Шаблоны не найдены")
            return
        
        # Создаём клавиатуру с категориями
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        
        # Кнопки категорий
        categories = template_service.get_all_categories()
        category_names = {
            'cat_size': '📏 Размеры',
            'cat_delivery': '🚚 Доставка',
            'cat_pvz': '🏪 ПВЗ',
            'cat_return': '🔄 Возврат',
            'cat_price': '💰 Цены',
            'cat_emotion': '😍 Эмоции'
        }
        
        category_buttons = []
        for category in categories:
            display_name = category_names.get(category, category)
            category_buttons.append(display_name)
        
        # Добавляем кнопки категорий в 2 колонки
        for i in range(0, len(category_buttons), 2):
            row = category_buttons[i:i+2]
            markup.add(*row)
        
        # Кнопки навигации
        nav_buttons = []
        if page > 0:
            nav_buttons.append("◀️ Назад")
        
        if end_idx < len(all_popular):
            nav_buttons.append("Вперед ▶️")
        
        if nav_buttons:
            markup.add(*nav_buttons)
        
        markup.add("📋 Главное меню")
        
        # Формируем сообщение
        message_text = "📚 *Шаблоны ответов*\n\n"
        
        # Добавляем информацию о странице
        total_templates = template_service.get_template_count()
        total_pages = (total_templates + items_per_page - 1) // items_per_page
        
        if total_pages > 1:
            message_text += f"Страница {page + 1} из {total_pages}\n\n"
        
        # Показываем шаблоны текущей страницы
        for i, template in enumerate(current_page_templates, start=1):
            formatted = template_service.format_template_for_display(template)
            
            # Номер шаблона с учётом страницы
            template_num = start_idx + i
            
            message_text += f"{template_num}. {formatted['display_title']}\n"
            
            # Добавляем категорию
            message_text += f"   Категория: {formatted['category_display']}\n"
            
            # Добавляем теги если есть
            if formatted.get('display_tags'):
                message_text += f"   Теги: {formatted['display_tags']}\n"
            
            # Добавляем предпросмотр текста
            preview = formatted.get('preview_text', '')
            if preview:
                message_text += f"   📝 {preview}\n"
            
            message_text += "\n"
        
        # Инструкции
        message_text += "🔍 *Как использовать:*\n"
        message_text += "• Нажмите на категорию для фильтрации\n"
        message_text += "• Используйте кнопки навигации\n"
        message_text += "• Или напишите /search [запрос] для поиска\n"
        
        bot.send_message(
            message.chat.id,
            message_text,
            parse_mode="Markdown",
            reply_markup=markup
        )
        
        logger.info(f"Показаны шаблоны для user={message.from_user.id}, page={page}")
        
    except Exception as e:
        logger.error(f"Ошибка в /templates: {e}", exc_info=True)
        bot.reply_to(message, "❌ Произошла ошибка при загрузке шаблонов")


def handle_template_search(bot, message, template_service):
    """
    Обработчик поиска шаблонов (/search [запрос])
    
    Args:
        bot: Экземпляр telebot.TeleBot
        message: Объект сообщения
        template_service: Экземпляр TemplateService
    """
    try:
        # Извлекаем поисковый запрос из сообщения
        search_query = message.text.replace('/search', '').strip()
        
        if not search_query:
            bot.reply_to(message, "🔍 *Использование:* /search [запрос]\n\nПример: /search доставка")
            return
        
        # Выполняем поиск
        results = template_service.search_templates(search_query, limit=10)
        
        if not results:
            bot.reply_to(
                message,
                f"🔍 По запросу \"{search_query}\" ничего не найдено.\n\n"
                f"Попробуйте другие ключевые слова:\n"
                f"• доставка\n• размер\n• возврат\n• цена"
            )
            return
        
        # Формируем сообщение с результатами
        message_text = f"🔍 *Результаты поиска: \"{search_query}\"*\n\n"
        message_text += f"Найдено шаблонов: {len(results)}\n\n"
        
        for i, template in enumerate(results, start=1):
            formatted = template_service.format_template_for_display(template)
            
            message_text += f"{i}. {formatted['display_title']}\n"
            message_text += f"   Категория: {formatted['category_display']}\n"
            
            if formatted.get('display_tags'):
                message_text += f"   Теги: {formatted['display_tags']}\n"
            
            # Показываем фрагмент текста с подсветкой запроса
            text_lower = template['text'].lower()
            query_lower = search_query.lower()
            
            if query_lower in text_lower:
                pos = text_lower.find(query_lower)
                start = max(0, pos - 20)
                end = min(len(template['text']), pos + len(search_query) + 20)
                
                fragment = template['text'][start:end]
                if start > 0:
                    fragment = "..." + fragment
                if end < len(template['text']):
                    fragment = fragment + "..."
                
                message_text += f"   📝 {fragment}\n"
            
            message_text += "\n"
        
        # Создаём клавиатуру для возврата
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📚 Все шаблоны", "📋 Главное меню")
        
        bot.send_message(
            message.chat.id,
            message_text,
            parse_mode="Markdown",
            reply_markup=markup
        )
        
        logger.info(f"Поиск шаблонов: user={message.from_user.id}, query='{search_query}', results={len(results)}")
        
    except Exception as e:
        logger.error(f"Ошибка поиска шаблонов: {e}", exc_info=True)
        bot.reply_to(message, "❌ Произошла ошибка при поиске")


def handle_template_category(bot, message, template_service, category_key: str):
    """
    Обработчик выбора категории шаблонов
    
    Args:
        bot: Экземпляр telebot.TeleBot
        message: Объект сообщения
        template_service: Экземпляр TemplateService
        category_key: Ключ категории (cat_size, cat_delivery и т.д.)
    """
    try:
        # Получаем шаблоны категории
        templates = template_service.get_templates_by_category(category_key)
        
        if not templates:
            bot.reply_to(message, f"📭 В этой категории пока нет шаблонов")
            return
        
        # Названия категорий для отображения
        category_display_names = {
            'cat_size': '📏 Размеры',
            'cat_delivery': '🚚 Доставка',
            'cat_pvz': '🏪 Пункты выдачи',
            'cat_return': '🔄 Возврат и обмен',
            'cat_price': '💰 Цены и акции',
            'cat_emotion': '😍 Эмоции и благодарность'
        }
        
        display_name = category_display_names.get(category_key, category_key)
        
        # Формируем сообщение
        message_text = f"{display_name}\n\n"
        message_text += f"Шаблонов в категории: {len(templates)}\n\n"
        
        for i, template in enumerate(templates, start=1):
            formatted = template_service.format_template_for_display(template)
            
            message_text += f"{i}. {formatted['display_title']}\n"
            
            # Предпросмотр текста
            preview = formatted.get('preview_text', '')
            if preview:
                message_text += f"   📝 {preview}\n"
            
            message_text += "\n"
        
        # Кнопки навигации
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📚 Все шаблоны", "🔍 Поиск", "📋 Главное меню")
        
        bot.send_message(
            message.chat.id,
            message_text,
            parse_mode="Markdown",
            reply_markup=markup
        )
        
        logger.info(f"Показана категория: user={message.from_user.id}, category={category_key}")
        
    except Exception as e:
        logger.error(f"Ошибка показа категории {category_key}: {e}", exc_info=True)
        bot.reply_to(message, "❌ Произошла ошибка при загрузке категории")


def register(bot, config):
    """
    Регистрирует хендлеры для команд шаблонов
    
    Args:
        bot: Экземпляр telebot.TeleBot
        config: Конфигурация из core.config.Config
    """
    # Импортируем здесь чтобы избежать циклических импортов
    from core.services import TemplateService
    from data.templates_database import TEMPLATES_DATABASE
    
    # Создаём сервис
    template_service = TemplateService(TEMPLATES_DATABASE)
    
    # Хранилище для состояния пользователей (страница)
    user_pages = {}
    
    @bot.message_handler(commands=['templates', 'шаблоны'])
    def templates_wrapper(message):
        """Обёртка для команды /templates"""
        user_id = message.from_user.id
        page = user_pages.get(user_id, 0)
        handle_templates(bot, message, template_service, page)
    
    @bot.message_handler(commands=['search'])
    def search_wrapper(message):
        """Обёртка для команды /search"""
        handle_template_search(bot, message, template_service)
    
    @bot.message_handler(func=lambda message: message.text in [
        "📏 Размеры", "🚚 Доставка", "🏪 ПВЗ", 
        "🔄 Возврат", "💰 Цены", "😍 Эмоции"
    ])
    def category_button_wrapper(message):
        """Обработчик кнопок категорий"""
        # Сопоставляем отображаемые имена с ключами категорий
        category_mapping = {
            "📏 Размеры": "cat_size",
            "🚚 Доставка": "cat_delivery",
            "🏪 ПВЗ": "cat_pvz",
            "🔄 Возврат": "cat_return",
            "💰 Цены": "cat_price",
            "😍 Эмоции": "cat_emotion"
        }
        
        category_key = category_mapping.get(message.text)
        if category_key:
            handle_template_category(bot, message, template_service, category_key)
    
    @bot.message_handler(func=lambda message: message.text in ["◀️ Назад", "Вперед ▶️"])
    def navigation_wrapper(message):
        """Обработчик навигации по страницам"""
        user_id = message.from_user.id
        current_page = user_pages.get(user_id, 0)
        
        if message.text == "◀️ Назад" and current_page > 0:
            user_pages[user_id] = current_page - 1
        elif message.text == "Вперед ▶️":
            user_pages[user_id] = current_page + 1
        
        handle_templates(bot, message, template_service, user_pages.get(user_id, 0))
    
    @bot.message_handler(func=lambda message: message.text == "📚 Все шаблоны")
    def all_templates_wrapper(message):
        """Обработчик кнопки 'Все шаблоны'"""
        user_id = message.from_user.id
        user_pages[user_id] = 0  # Сбрасываем на первую страницу
        handle_templates(bot, message, template_service, 0)
    
    logger.info("Хендлеры шаблонов зарегистрированы")
    print("✅ Хендлер /templates зарегистрирован")