from telebot import types
from core.config import get_bot_config
import random

def register_handlers_track(bot):
    @bot.message_handler(commands=['track'])
    def track_handler(message):
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            bot.reply_to(message, "❌ /track 123456789\n9 цифр трек-номер WB")
            return
        
        order_id = parts[1].strip()
        if not (order_id.isdigit() and len(order_id) == 9):
            bot.reply_to(message, "❌ 9 цифр, пример: /track 123456789")
            return
        
        # Mock WB статусы (реалистичные)
        statuses = [
            ("📦 Сформирован", "Готов к отправке"),
            ("🚚 В пути", "Постамат 15.02"),
            ("🏪 На ПВЗ", "Самовывоз готов"),
            ("✅ Выдан", "Клиент забрал"),
            ("❌ Отмена", "Возврат денег")
        ]
        status, detail = random.choice(statuses)
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💬 Шаблон ответа", callback_data=f"track_{order_id}_{status}"))
        markup.add(types.InlineKeyboardButton("📱 Проверить WB", callback_data="wb_link"))
        markup.add(types.InlineKeyboardButton("⭐ Отзыв", callback_data="review"))
        
        bot.reply_to(message, 
            f"📋 Заказ #{order_id}\n"
            f"{status}\n"
            f"{detail}\n\n"
            f"⏰ {random.randint(1, 3)} мин назад",
            reply_markup=markup)
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('track_'))
    def track_callback(call):
        _, order_id, status = call.data.split('_', 2)
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"📝 Шаблон для '{status}':\n'Заказ #{order_id} {status.lower()}. Ожидайте...'")
