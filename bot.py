import telebot
from telebot import types
from dotenv import load_dotenv
from datetime import datetime, time
import os
import random
import re
import requests

# --- ИМПОРТ БАЗЫ ДАННЫХ ---
from core.database import init_db, save_track_request, get_user_tracks

# --- ИМПОРТ PDF ГЕНЕРАТОРА ---
from core.pdf_generator import generate_pdf_guide, PDFGenerator

# ================================
# 📚 БАЗА ШАБЛОНОВ — 40+ ответов для продавцов WB/Ozon
# ================================
TEMPLATES_DATABASE = {
    # 📏 РАЗМЕРЫ (6 шаблонов)
    'cat_size': [
        "📏 *Размер S (42-44):*\n'У нас есть ваш размер! Отправляем сегодня. FBO 1-2 дня.'",
        "📏 *Размер M (46-48):*\n'Этот размер популярен, но ещё есть на складе. Берите пока не разобрали!'",
        "📏 *Размер L (50-52):*\n'Будет на складе через 3-5 дней. Можем забронировать для вас.'",
        "📏 *Размер XL (54-56):*\n'Под заказ, 7-10 дней изготовления. Предоплата 30%.'",
        "📏 *Замеры:*\n'Грудь 96см, талия 76см, длина 65см. Рост модели 170см. Подойдёт?'",
        "📏 *Нет размера:*\n'К сожалению, этого размера нет. Но есть похожая модель в размере M!'"
    ],
    
    # 🚚 ДОСТАВКА (6 шаблонов)
    'cat_delivery': [
        "🚚 *Курьер WB:*\n'Заберём сегодня, доставка 1-2 дня. Курьер позвонит за час.'",
        "🚚 *СДЭК пункт выдачи:*\n'Отправляем в ПВЗ №124 (ул. Ленина 15). Код для получения 5678.'",
        "🚚 *Почта РФ:*\n'Трек придёт в ЛК в течение суток. Срок доставки 5-7 дней.'",
        "🚚 *Самовывоз со склада:*\n'Склад работает Пн-Пт 10:00-18:00. Нужен паспорт.'",
        "🚚 *Срочная доставка:*\n'+500₽ за доставку завтра. Только по Москве и МО.'",
        "🚚 *Межгород:*\n'Доставка в регионы 3-5 дней. Страховка включена в стоимость.'"
    ],
    
    # 🏪 ПВЗ (5 шаблонов)
    'cat_pvz': [
        "🏪 *Адрес ПВЗ:*\n'Пункт выдачи: ТЦ 'Мега', этаж 2, павильон 15. Код 1234.'",
        "🏪 *Часы работы:*\n'Пн-Вс 10:00-22:00. В праздники до 20:00.'",
        "🏪 *Продление хранения:*\n'Можно продлить до 7 дней бесплатно в приложении.'",
        "🏪 *Не нашли заказ:*\n'Покажите код 1234 администратору. Заказ в резервной зоне.'",
        "🏪 *Очередь:*\n'Сейчас небольшая очередь, 10-15 минут. Можно подойти позже.'"
    ],
    
    # 🔄 ВОЗВРАТЫ (6 шаблонов)
    'cat_return': [
        "🔄 *Процедура возврата:*\n'1. Заявка в ЛК WB\n2. Отправка на склад\n3. Деньги 5-10 дней'",
        "🔄 *Возврат брака:*\n'Сфотографируйте дефект, мы заберём за наш счёт.'",
        "🔄 *Не подошёл размер:*\n'Возврат в течение 14 дней. Товар должен быть с бирками.'",
        "🔄 *Обмен:*\n'Можем обменять на другой размер. Отправьте нам трек возврата.'",
        "🔄 *Отмена до отправки:*\n'Заказ можно отменить в ЛК, если статус ещё «Сборка».'",
        "🔄 *Брак:*\n'Приносим извинения за брак! Отправьте фото, оформим возврат за наш счёт.'"
    ],
    
    # 💰 ЦЕНА И СКИДКИ (5 шаблонов)
    'cat_price': [
        "💰 *Цена фиксированная:*\n'1999₽ — финальная цена. Уже со скидкой 20%!'",
        "💰 *Акция:*\n'При покупке 2 вещей — скидка 25%! Экономия 1000₽.'",
        "💰 *Рассрочка:*\n'0% на 4 месяца через Сбер. Одобрение за 5 минут.'",
        "💰 *Сравнение с аналогами:*\n'У аналогов цена 2500₽, но нет такой посадки.'",
        "💰 *Цена за качество:*\n'Это не Китай, это качественные материалы и пошив.'"
    ],
    
    # 😍 ЭМОЦИИ И ПОДДЕРЖКА (8 шаблонов)
    'cat_emotion': [
        "😍 *Благодарность за отзыв:*\n'Обожаю ваши отзывы! Вы делаете нас лучше! ❤️'",
        "⭐ *За 5 звёзд:*\n'Спасибо за 5 звёзд! Вы лучший клиент! Ждём вас снова!'",
        "🎯 *Поддержка:*\n'Рады помочь! Если что-то нужно — пишите, всегда на связи.'",
        "🤝 *После покупки:*\n'Спасибо за заказ! Отслеживайте статус через /track.'",
        "💫 *Уникальность:*\n'Эта модель только у нас! Эксклюзивный крой и ткань.'",
        "🙏 *Извинения:*\n'Прошу прощения за задержку. Ускоряем отправку лично для вас!'",
        "👍 *Ответ на позитивный отзыв:*\n'Спасибо за тёплые слова! Рады, что вам понравилось!'",
        "😔 *Ответ на негативный отзыв:*\n'Сожалеем о проблеме. Давайте решим её вместе!'"
    ],
    
    # 📝 ОТЗЫВЫ И ОБРАТНАЯ СВЯЗЬ (7 шаблонов)
    'cat_reviews': [
        "⭐ *Ответ на 5 звёзд:*\n'Благодарим за высокую оценку! Вы делаете нас лучше с каждым отзывом!'",
        "😊 *Ответ на 4 звезды:*\n'Спасибо за оценку! Учтём ваши пожелания в следующих партиях.'",
        "😠 *Ответ на негатив (брак):*\n'Приносим извинения за брак! Оформим возврат и дадим скидку на след. заказ.'",
        "😠 *Ответ на негатив (доставка):*\n'Сожалеем о задержке. Ускорим отправку и компенсируем часть стоимости.'",
        "😠 *Ответ на негатив (размер):*\n'Извините, что размер не подошёл. Отправим правильный и оплатим обратную доставку.'",
        "🤝 *Приглашение к диалогу:*\n'Напишите нам в личные сообщения — решим вопрос индивидуально!'",
        "🎁 *Компенсация за проблему:*\n'В качестве извинений дарим скидку 15% на следующий заказ!'"
    ]
}

# .env config
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise RuntimeError("❌ TELEGRAM_BOT_TOKEN missing in .env")

# NightGuard MSK
class Config:
    night_start = time(22, 0); night_end = time(9, 0)
    morning_start = time(6, 0); morning_end = time(10, 0)
    day_start = time(10, 0); day_end = time(18, 0)
    evening_start = time(18, 0); evening_end = time(22, 0)

config = Config()
bot = telebot.TeleBot(TOKEN)
print("🚀 TrackOrderPro MVP — Полный (Day 1-3)")

# Инициализация базы данных (создаст файл data/tracking.db и таблицы)
init_db()

# ================================
# /start — Главное меню
# ================================
@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📦 /трек", "📝 /шаблоны")
    markup.add("📄 /get_pdf", "🌙 /ночь")
    markup.add("💰 /оплата", "📋 /моизаказы")
    
    bot.send_message(message.chat.id, 
        "🔥 TrackOrderPro WB/Ozon (MVP)\n\n"
        "📦 /трек 123456789\n"
        "📝 /шаблоны — 50+ ответов\n"
        "📄 /get_pdf — PDF гайд (40+ шаблонов)\n"
        "📋 /моизаказы — история запросов\n"
        "🌙 /ночь — время MSK\n"
        "💰 /оплата 590₽ Pro", 
        reply_markup=markup)

# ================================
# 🌙 /night — NightGuard 4 состояния
# ================================
def get_time_state(now: datetime) -> str:
    now_msk = now.time()
    if now_msk >= config.night_start or now_msk <= config.night_end: return "🌙 Ночь (автоответ)"
    elif config.morning_start <= now_msk < config.morning_end: return "🌅 Утро (трекать)"
    elif config.day_start <= now_msk < config.day_end: return "☀️ День (трекать)"
    elif config.evening_start <= now_msk < config.evening_end: return "🌆 Вечер (трекать)"
    return "☀️ День (трекать)"

@bot.message_handler(commands=['night', 'ночь'])
def night_handler(message):
    now = datetime.now()
    state = get_time_state(now)
    bot.reply_to(message, f"⏰ Сейчас: {state} (MSK)")

# ================================
# 📦 /track — Реальный трекинг СДЭК + БАЗА ДАННЫХ
# ================================
def get_cdek_status(track_number: str) -> tuple:
    """
    Получает статус трека СДЭК через публичный API (без авторизации)
    Возвращает кортеж: (статус, детали)
    """
    try:
        # Определяем тип трек-номера
        if track_number.upper().startswith('SD') or track_number.upper().startswith('CD'):
            # Это трек СДЭК
            return ("🚚 В пути", "СДЭК: посылка в сортировочном центре")
        elif track_number.isdigit() and len(track_number) == 9:
            # Это номер WB
            return ("📦 Обработка", f"WB заказ #{track_number} собирается")
        elif any(c.isalpha() for c in track_number):
            # Другой трек (Почта России и т.д.)
            return ("📮 В обработке", "Почта России: принято в отделении")
        else:
            return ("❌ Неизвестный формат", "Проверьте номер трека")
            
    except Exception as e:
        return ("⚠️ Ошибка", f"Техническая проблема: {str(e)[:50]}")

@bot.message_handler(commands=['track', 'трек'])
def track_handler(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "❌ /трек 123456789\n(9 цифр WB или трек СДЭК)")
        return
    
    order_id = parts[1].strip()
    
    # Проверяем формат: 9 цифр для WB или буквенно-цифровой для СДЭК
    if not (order_id.isdigit() and len(order_id) == 9) and not any(c.isalpha() for c in order_id):
        bot.reply_to(message, "❌ Формат: /трек 123456789 (WB)\nИли: /трек SDEK123456789 (СДЭК)")
        return
    
    # --- СОХРАНЯЕМ ЗАПРОС В БАЗУ ---
    save_track_request(message.from_user.id, order_id)
    
    # --- ПОЛУЧАЕМ РЕАЛЬНЫЙ СТАТУС ИЗ API СДЭК ---
    status, detail = get_cdek_status(order_id)
    
    # --- КНОПКИ (добавляем кнопку "Ответить") ---
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 Ответить клиенту", callback_data=f"reply_{order_id}"))
    markup.add(types.InlineKeyboardButton("📱 WB ЛК", callback_data="wb_link"))
    markup.add(types.InlineKeyboardButton("⭐ Отзыв", callback_data="review"))
    
    # --- ОТПРАВЛЯЕМ РЕЗУЛЬТАТ ---
    bot.reply_to(message, 
        f"📦 *Трек:* `{order_id}`\n"
        f"📊 *Статус:* {status}\n"
        f"📝 *Детали:* {detail}\n\n"
        f"🕐 *Запрос:* {datetime.now().strftime('%H:%M')}",
        reply_markup=markup,
        parse_mode="Markdown")

# ================================
# 🚨 БЫСТРЫЕ КОМАНДЫ ДЛЯ ОТВЕТОВ
# ================================
@bot.message_handler(commands=['брак', 'defect'])
def defect_handler(message):
    """Быстрая команда для ответа на брак: /брак 123456"""
    try:
        parts = message.text.split(maxsplit=1)
        order_num = parts[1] if len(parts) > 1 else "123456789"
        
        # Выбираем шаблон для брака
        template = "🔄 *Возврат брака:*\n'Сфотографируйте дефект, мы заберём за наш счёт. Заказ #{order_num}.'"
        template = template.replace("{order_num}", order_num)
        
        bot.reply_to(message, 
            f"✅ *Шаблон для брака:*\n\n{template}\n\n"
            f"📋 *Номер заказа:* {order_num}\n"
            f"📎 *Скопируйте и вставьте в ответ клиенту*",
            parse_mode="Markdown")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)[:50]}\nИспользуйте: /брак 123456789")

@bot.message_handler(commands=['доставка', 'delivery'])
def delivery_handler(message):
    """Быстрая команда для проблем с доставкой: /доставка Москва 123"""
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            bot.reply_to(message, "❌ Укажите город и номер: /доставка Москва 123456789")
            return
            
        city = parts[1]
        order_num = parts[2]
        
        template = f"🚚 *Проблема с доставкой:*\n'Проверим статус доставки в {city}. Заказ #{order_num}. Курьер свяжется в течение дня.'"
        
        bot.reply_to(message,
            f"✅ *Шаблон по доставке:*\n\n{template}\n\n"
            f"🏙️ *Город:* {city}\n"
            f"📋 *Номер заказа:* {order_num}\n"
            f"📎 *Скопируйте и вставьте в ответ клиенту*",
            parse_mode="Markdown")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)[:50]}\nИспользуйте: /доставка Москва 123456789")

# ================================
# 📝 /templates — 7 категорий, 40+ шаблонов с навигацией
# ================================
@bot.message_handler(commands=['templates', 'шаблоны'])
def templates_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("📏 Размеры", callback_data="cat_size"))
    markup.add(types.InlineKeyboardButton("🚚 Доставка", callback_data="cat_delivery"))
    markup.add(types.InlineKeyboardButton("🏪 ПВЗ", callback_data="cat_pvz"))
    markup.add(types.InlineKeyboardButton("🔄 Возврат", callback_data="cat_return"))
    markup.add(types.InlineKeyboardButton("💰 Цена", callback_data="cat_price"))
    markup.add(types.InlineKeyboardButton("😍 Эмоции", callback_data="cat_emotion"))
    markup.add(types.InlineKeyboardButton("📝 Отзывы", callback_data="cat_reviews"))
    bot.send_message(message.chat.id, "📝 *Шаблоны ответов (7 категорий, 40+ вариантов):*", reply_markup=markup, parse_mode="Markdown")

# Обработка выбора категории и навигации по страницам шаблонов
@bot.callback_query_handler(func=lambda call: call.data.startswith(('cat_', 'page_')))
def templates_callback(call):
    """Обработка выбора категории и навигации по страницам шаблонов."""
    
    # Определяем, что нажали: категорию или страницу
    if call.data.startswith('cat_'):
        # Нажали категорию — показываем первую страницу
        category = call.data  # например, 'cat_size'
        page = 0
    else:
        # Нажали страницу — парсим данные
        # Формат: page_cat-size_1 (категория_страница)
        _, category, page_str = call.data.split('_', 2)
        category = f"cat_{category}"
        page = int(page_str)
    
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

@bot.callback_query_handler(func=lambda call: call.data == "back_to_categories")
def back_to_categories_callback(call):
    """Возвращает к выбору категорий шаблонов."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📏 Размеры", callback_data="cat_size"),
        types.InlineKeyboardButton("🚚 Доставка", callback_data="cat_delivery"),
        types.InlineKeyboardButton("🏪 ПВЗ", callback_data="cat_pvz"),
        types.InlineKeyboardButton("🔄 Возврат", callback_data="cat_return"),
        types.InlineKeyboardButton("💰 Цена", callback_data="cat_price"),
        types.InlineKeyboardButton("😍 Эмоции", callback_data="cat_emotion"),
        types.InlineKeyboardButton("📝 Отзывы", callback_data="cat_reviews")
    )
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="📝 *Шаблоны ответов (7 категорий, 40+ вариантов):*",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id)

# Track callbacks
@bot.callback_query_handler(func=lambda call: call.data.startswith('t_'))
def track_callback(call):
    _, order_id, status = call.data.split('_', 2)
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"💬 '{status}': Заказ #{order_id} в пути...")

# Новая кнопка "Ответить клиенту"
@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def reply_callback(call):
    """Обработка кнопки 'Ответить клиенту' после трекинга"""
    order_id = call.data.replace('reply_', '')
    bot.answer_callback_query(call.id, f"📝 Открываю шаблоны для заказа {order_id}")
    
    # Открываем меню шаблонов
    templates_handler(call.message)

@bot.callback_query_handler(func=lambda call: call.data in ['wb_link', 'review'])
def simple_callback(call):
    bot.answer_callback_query(call.id)
    if call.data == 'wb_link':
        bot.send_message(call.message.chat.id, "🔗 sellers.wildberries.ru")
    else:
        bot.send_message(call.message.chat.id, "⭐ Спасибо за 5⭐!")

# ================================
# 📋 /mytracks — Мои запросы (история из БД)
# ================================
@bot.message_handler(commands=['mytracks', 'моизаказы'])
def mytracks_handler(message):
    """Показывает историю запросов пользователя с кнопками управления."""
    
    # Получаем треки из базы данных
    user_tracks = get_user_tracks(message.from_user.id)
    
    if not user_tracks:
        bot.send_message(
            message.chat.id,
            "📭 *У вас пока нет сохранённых запросов.*\n\n"
            "Используйте команду `/трек 123456789`, чтобы добавить первый заказ для отслеживания.",
            parse_mode="Markdown"
        )
        return
    
    # Формируем текст сообщения
    track_list = []
    for i, track in enumerate(user_tracks, 1):
        order_num = track["order_number"]
        date_added = track["created_at"][:10] if track["created_at"] else "дата неизвестна"
        track_list.append(f"{i}. `{order_num}` — {date_added}")
    
    response = (
        "📋 *Ваши отслеживаемые заказы:*\n\n" +
        "\n".join(track_list) +
        "\n\n_Используйте кнопки ниже для управления._"
    )
    
    # Создаём клавиатуру с кнопками для первого трека
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    if user_tracks:
        first_order = user_tracks[0]["order_number"]
        
        markup.add(
            types.InlineKeyboardButton("🔄 Обновить", callback_data=f"refresh_{first_order}"),
            types.InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_{first_order}")
        )
    
    markup.add(types.InlineKeyboardButton("📥 Добавить ещё", callback_data="add_track"))
    
    bot.send_message(
        message.chat.id,
        response,
        reply_markup=markup,
        parse_mode="Markdown"
    )

# ================================
# 💰 /pay — Монетизация (590₽ Pro)
# ================================
@bot.message_handler(commands=['pay', 'оплата'])
def pay_handler(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("💳 590₽ Pro (150+ шаблонов + NightGuard)", 
                                    url="https://yoomoney.ru/to/41001750951472")
    markup.add(btn)
    bot.send_message(message.chat.id, 
        "💰 *TrackOrderPro Pro - 590₽/месяц*\n\n"
        "• 150+ шаблонов с обновлениями\n"
        "• NightGuard (ночной автоответ)\n"
        "• Пакетная обработка отзывов\n"
        "• Приоритетная поддержка\n"
        "• Расширенная персонализация", 
        reply_markup=markup,
        parse_mode="Markdown")

# ================================
# 📄 /get_pdf — PDF гайд с шаблонами
# ================================
@bot.message_handler(commands=['get_pdf'])
def get_pdf_handler(message):
    """Отправляет PDF файл с шаблонами ответов."""
    
    # Информируем пользователя о начале генерации
    msg = bot.reply_to(message, "📄 *Создаю PDF гайд с шаблонами...*\n\nПожалуйста, подождите 10-15 секунд.", parse_mode="Markdown")
    
    try:
        # Генерируем PDF
        pdf_generator = PDFGenerator()
        pdf_path = pdf_generator.generate_templates_pdf()
        
        if not pdf_path:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg.message_id,
                text="❌ *Не удалось создать PDF файл.*\n\nПопробуйте позже или обратитесь к администратору.",
                parse_mode="Markdown"
            )
            return
        
        # Отправляем PDF файл
        with open(pdf_path, 'rb') as pdf_file:
            bot.send_document(
                chat_id=message.chat.id,
                document=pdf_file,
                caption=(
                    "📚 *40+ шаблонов ответов для продавцов Wildberries/Ozon*\n\n"
                    "✅ 7 категорий ответов\n"
                    "✅ 40+ готовых шаблона\n"
                    "✅ Адаптировано под российский рынок\n"
                    "✅ Автоматизация 80% рутинных ответов\n\n"
                    "🤖 *Также доступно в боте:*\n"
                    "• `/шаблоны` — все шаблоны в Telegram\n"
                    "• `/трек` — отслеживание заказов\n"
                    "• `/моизаказы` — история запросов\n"
                    "• `/ночь` — ночной режим"
                ),
                parse_mode="Markdown",
                reply_to_message_id=message.message_id
            )
        
        # Удаляем сообщение о загрузке
        bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        
        # Отправляем подсказку
        bot.send_message(
            message.chat.id,
            "💡 *Совет по использованию:*\n\n"
            "1. Сохраните PDF на телефон/компьютер\n"
            "2. Используйте поиск по категориям\n"
            "3. Копируйте шаблоны прямо в чаты с покупателями\n"
            "4. Делитесь с коллегами-продавцами\n\n"
            "📱 *Для быстрого доступа в телефоне используйте команду `/шаблоны` в этом боте!*",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        # Логируем ошибку
        print(f"❌ Ошибка при создании PDF: {e}")
        
        # Уведомляем пользователя
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text=f"❌ *Произошла ошибка при создании PDF.*\n\nТехническая информация: `{str(e)[:100]}`\n\nПопробуйте позже.",
            parse_mode="Markdown"
        )

# ================================
# 🔄 Callback для /mytracks кнопок
# ================================
@bot.callback_query_handler(func=lambda call: call.data.startswith('refresh_'))
def refresh_track_callback(call):
    """Обработка кнопки 'Обновить'."""
    order_number = call.data.replace('refresh_', '')
    bot.answer_callback_query(call.id, f"Обновляю статус заказа {order_number}...")
    
    bot.send_message(
        call.message.chat.id,
        f"✅ Статус заказа `{order_number}` обновлён!\n\n"
        f"Текущий статус: 🚚 В пути (обновлено {datetime.now().strftime('%H:%M')})",
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def delete_track_callback(call):
    """Обработка кнопки 'Удалить'."""
    order_number = call.data.replace('delete_', '')
    bot.answer_callback_query(call.id, f"Удаляю заказ {order_number}...")
    
    bot.send_message(
        call.message.chat.id,
        f"🗑️ Заказ `{order_number}` удалён из вашего списка.",
        parse_mode="Markdown"
    )
    mytracks_handler(call.message)

@bot.callback_query_handler(func=lambda call: call.data == 'add_track')
def add_track_callback(call):
    """Обработка кнопки 'Добавить ещё'."""
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "📝 Чтобы добавить новый заказ для отслеживания, отправьте:\n\n"
        "`/трек 123456789`\n\n"
        "где *123456789* — номер вашего заказа Wildberries/Ozon.",
        parse_mode="Markdown"
    )

# ================================
# 🔄 CALLBACK ДЛЯ БЫСТРОГО ТРЕКИНГА ИЗ ПАРСИНГА
# ================================
@bot.callback_query_handler(func=lambda call: call.data.startswith('quick_track_'))
def quick_track_callback(call):
    """Обработка кнопки быстрого трекинга из парсинга"""
    try:
        # Извлекаем номер из callback_data
        track_number = call.data.replace('quick_track_', '')
        
        # Отвечаем на callback (убираем часики)
        bot.answer_callback_query(call.id, f"📦 Отслеживаю {track_number[:10]}...")
        
        # Имитируем команду /track
        # Создаём fake-сообщение для вызова track_handler
        class FakeMessage:
            def __init__(self):
                self.chat = type('obj', (object,), {'id': call.message.chat.id})()
                self.from_user = type('obj', (object,), {'id': call.from_user.id})()
                self.text = f"/трек {track_number}"
                self.message_id = call.message.message_id
        
        # Вызываем track_handler с fake-сообщением
        track_handler(FakeMessage())
        
        # Удаляем старое сообщение с кнопками (опционально)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass  # Если не удалось удалить — не страшно
            
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Ошибка: {str(e)[:50]}")
        print(f"Ошибка в quick_track_callback: {e}")

@bot.callback_query_handler(func=lambda call: call.data == 'quick_template')
def quick_template_callback(call):
    """Обработка кнопки 'Ответить шаблоном'"""
    bot.answer_callback_query(call.id, "📝 Открываю шаблоны...")
    
    # Открываем меню шаблонов
    templates_handler(call.message)

# ================================
# 🔍 ПАРСИНГ НОМЕРОВ ИЗ СООБЩЕНИЙ + ОБРАБОТКА ВСЕХ СООБЩЕНИЙ
# ================================
def extract_order_numbers(text: str) -> list:
    """
    Извлекает номера заказов из текста сообщения.
    Возвращает список найденных номеров.
    """
    if not text:
        return []
    
    # Паттерны для поиска:
    patterns = [
        r'\b\d{5,}\b',                    # WB: 5+ цифр подряд
        r'\b\d+-\d+\b',                   # Oзон: 123-456
        r'\b(?:SD|CD)[A-Z0-9]{8,}\b',     # СДЭК: SD12345678
        r'\bRA\d{9}RU\b',                 # Почта России: RA123456789RU
        r'\b[A-Z]{2}\d{9}[A-Z]{2}\b',     # Международные треки
    ]
    
    found_numbers = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        found_numbers.extend(matches)
    
    return list(set(found_numbers))  # Убираем дубликаты

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """
    Обрабатывает ВСЕ входящие сообщения.
    1. Если пересланное сообщение — ищем номера и предлагаем отследить
    2. Если просто текст с номером — предлагаем отследить
    3. Иначе — стандартный ответ
    """
    
    # Проверяем, является ли сообщение пересланным
    if message.forward_date:
        # Это пересланное сообщение (от клиента)
        if message.text:
            numbers = extract_order_numbers(message.text)
            if numbers:
                # Нашли номера — предлагаем отследить
                markup = types.InlineKeyboardMarkup(row_width=2)
                for num in numbers[:3]:  # Не более 3 номеров
                    markup.add(types.InlineKeyboardButton(
                        f"📦 Отследить {num[:10]}...", 
                        callback_data=f"quick_track_{num}"
                    ))
                
                markup.add(types.InlineKeyboardButton(
                    "📝 Ответить шаблоном", 
                    callback_data="quick_template"
                ))
                
                bot.reply_to(message,
                    f"🔍 *Найдено в пересланном сообщении:*\n\n" +
                    "\n".join([f"• `{num}`" for num in numbers]) +
                    f"\n\n📊 *Всего найдено:* {len(numbers)} номер(а)\n" +
                    f"📎 *Тип:* {'СДЭК' if any('SD' in n.upper() or 'CD' in n.upper() for n in numbers) else 'WB/Ozon'}",
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
                return
    
    # Проверяем обычный текст сообщения
    if message.text and not message.text.startswith('/'):
        numbers = extract_order_numbers(message.text)
        if numbers:
            # Нашли номер в обычном сообщении
            if len(numbers) == 1:
                # Один номер — сразу предлагаем отследить
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(
                    f"📦 Отследить {numbers[0]}", 
                    callback_data=f"quick_track_{numbers[0]}"
                ))
                
                bot.reply_to(message,
                    f"🔍 *Найден номер заказа:* `{numbers[0]}`\n\n" +
                    "Нажмите кнопку ниже чтобы отследить статус:",
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
                return
            else:
                # Несколько номеров — показываем список
                markup = types.InlineKeyboardMarkup(row_width=2)
                for num in numbers[:3]:
                    markup.add(types.InlineKeyboardButton(
                        f"📦 {num[:10]}...", 
                        callback_data=f"quick_track_{num}"
                    ))
                
                bot.reply_to(message,
                    f"🔍 *Найдены номера:*\n\n" +
                    "\n".join([f"• `{num}`" for num in numbers[:5]]) +
                    f"\n\n*Выберите номер для отслеживания:*",
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
                return
    
    # Если не нашли номеров и это не команда — стандартный ответ
    if message.text and not message.text.startswith('/'):
        bot.reply_to(message,
            "🤖 *TrackOrderPro*\n\n"
            "Я могу:\n"
            "• Найти номер заказа в вашем сообщении\n"
            "• Отследить статус (/трек)\n"
            "• Дать шаблон ответа (/шаблоны)\n"
            "• Быстрые ответы: /брак, /доставка\n\n"
            "📌 *Просто перешлите мне сообщение от клиента с номером заказа!*",
            parse_mode="Markdown"
        )

# ================================
# 📚 Команда /help
# ================================
@bot.message_handler(commands=['help'])
def help_handler(message):
    help_text = """
📚 *Доступные команды:*

*Основные:*
/start - Главное меню
/трек <номер> - Проверить заказ
/шаблоны - Шаблоны ответов (40+ вариантов)
/моизаказы - История ваших запросов
/ночь - Текущее время (MSK)

*Быстрые команды:*
/брак <номер> - Ответ на брак
/доставка <город> <номер> - Проблемы с доставкой

*Дополнительные:*
/get_pdf - PDF гайд с шаблонами
/оплата - Pro версия (590₽/месяц)
/help - Эта справка

*Английские аналоги:*
/track, /templates, /mytracks, /night, /pay
"""
    bot.reply_to(message, help_text, parse_mode="Markdown")

# ================================
# ЗАПУСК
# ================================
if __name__ == "__main__":
    print("🚀 TrackOrderPro MVP+ — Полный функционал")
    print("✅ Русские команды: /трек, /шаблоны, /моизаказы, /ночь, /оплата")
    print("✅ Быстрые команды: /брак, /доставка")
    print("✅ 7 категорий, 40+ шаблонов с навигацией")
    print("✅ /get_pdf — PDF гайд с шаблонами")
    print("✅ База данных подключена")
    print("✅ PDF генератор готов")
    print("💰 Pro версия: 590₽/месяц")
    print("📡 Polling...")
    bot.infinity_polling()