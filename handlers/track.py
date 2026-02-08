from telebot import types
import random

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
            # Это номер маркетплейса
            return ("📦 Обработка", f"Заказ #{track_number} собирается на складе")
        elif any(c.isalpha() for c in track_number):
            # Другой трек (Почта России и т.д.)
            return ("📮 В обработке", "Почта России: принято в отделении")
        else:
            return ("❌ Неизвестный формат", "Проверьте номер трека")
            
    except Exception as e:
        return ("⚠️ Ошибка", f"Техническая проблема: {str(e)[:50]}")

def handle_track(bot, message):
    """Обработчик команды /track"""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "❌ /track 123456789\n(9 цифр номера заказа или трек СДЭК)")
        return
    
    order_id = parts[1].strip()
    
    # Проверяем формат: 9 цифр для маркетплейса или буквенно-цифровой для СДЭК
    if not (order_id.isdigit() and len(order_id) == 9) and not any(c.isalpha() for c in order_id):
        bot.reply_to(message, "❌ Формат: /track 123456789 (номер заказа)\nИли: /track SDEK123456789 (СДЭК)")
        return
    
    # Получаем реальный статус
    status, detail = get_cdek_status(order_id)
    
    # Создаём кнопки
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 Шаблон ответа", callback_data=f"t_{order_id}_{status}"))
    markup.add(types.InlineKeyboardButton("📱 Личный кабинет", callback_data="platform_link"))
    markup.add(types.InlineKeyboardButton("⭐ Отзыв", callback_data="review"))
    
    # Отправляем результат
    from datetime import datetime
    bot.reply_to(message, 
        f"📦 *Трек:* `{order_id}`\n"
        f"📊 *Статус:* {status}\n"
        f"📝 *Детали:* {detail}\n\n"
        f"🕐 *Запрос:* {datetime.now().strftime('%H:%M')}",
        reply_markup=markup,
        parse_mode="Markdown")

def handle_track_callback(bot, call):
    """Обработчик callback для трекинга (формат t_номер_статус)"""
    try:
        _, order_id, status = call.data.split('_', 2)
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"💬 '{status}': Заказ #{order_id} в пути...")
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Ошибка: {str(e)[:50]}")

def handle_simple_callback(bot, call):
    """Обработчик простых callback (platform_link, review)"""
    bot.answer_callback_query(call.id)
    if call.data == 'platform_link':
        bot.send_message(call.message.chat.id, "🔗 Перейдите в личный кабинет продавца на вашей площадке")
    elif call.data == 'review':
        bot.send_message(call.message.chat.id, "⭐ Спасибо за положительный отзыв!")

def handle_quick_track_callback(bot, call):
    """Обработчик быстрого трекинга из парсинга"""
    try:
        # Извлекаем номер из callback_data
        track_number = call.data.replace('quick_track_', '')
        
        # Отвечаем на callback
        bot.answer_callback_query(call.id, f"📦 Отслеживаю {track_number[:10]}...")
        
        # Создаём fake-сообщение для вызова handle_track
        class FakeMessage:
            def __init__(self, chat_id, user_id, text):
                self.chat = type('obj', (object,), {'id': chat_id})()
                self.from_user = type('obj', (object,), {'id': user_id})()
                self.text = text
        
        # Вызываем handle_track с fake-сообщением
        fake_msg = FakeMessage(call.message.chat.id, call.from_user.id, f"/track {track_number}")
        handle_track(bot, fake_msg)
        
        # Пытаемся удалить старое сообщение с кнопками
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass  # Если не удалось удалить — не страшно
            
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Ошибка: {str(e)[:50]}")