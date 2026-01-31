import telebot
from telebot import types
from dotenv import load_dotenv
from datetime import datetime, time
import os
import random

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

# ================================
# /start — Главное меню
# ================================
@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📦 /track", "📝 /templates")
    markup.add("🌙 /night", "💰 /pay")
    bot.send_message(message.chat.id, 
        "🔥 TrackOrderPro WB/Ozon (MVP)\n\n"
        "📦 /track 123456789\n"
        "📝 /templates — 50+ ответов\n"
        "🌙 /night — время MSK\n"
        "💰 /pay 300₽ Pro", 
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

@bot.message_handler(commands=['night'])
def night_handler(message):
    now = datetime.now()
    state = get_time_state(now)
    bot.reply_to(message, f"⏰ Сейчас: {state} (MSK)")

# ================================
# 📦 /track — Mock WB (9 цифр + кнопки)
# ================================
@bot.message_handler(commands=['track'])
def track_handler(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "❌ /track 123456789\n(9 цифр WB)")
        return
    order_id = parts[1].strip()
    if not (order_id.isdigit() and len(order_id) == 9):
        bot.reply_to(message, "❌ 9 цифр! Пример: /track 123456789")
        return
    
    statuses = [
        ("📦 Сформирован", "Готов к отправке"),
        ("🚚 В пути", "Постамат 15.02"),
        ("🏪 На ПВЗ", "Самовывоз"),
        ("✅ Выдан", "Клиент забрал"),
        ("❌ Отмена", "Возврат")
    ]
    status, detail = random.choice(statuses)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("💬 Шаблон", callback_data=f"t_{order_id}_{status}"))
    markup.add(types.InlineKeyboardButton("📱 WB", callback_data="wb_link"))
    markup.add(types.InlineKeyboardButton("⭐ Отзыв", callback_data="review"))
    
    bot.reply_to(message, 
        f"📋 #{order_id}\n"
        f"{status}\n"
        f"{detail}\n\n"
        f"⏰ {random.randint(1,59)} мин назад",
        reply_markup=markup)

# ================================
# 📝 /templates — 6 категорий WB
# ================================
@bot.message_handler(commands=['templates'])
def templates_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("📏 Размеры", callback_data="cat_size"))
    markup.add(types.InlineKeyboardButton("🚚 Доставка", callback_data="cat_delivery"))
    markup.add(types.InlineKeyboardButton("🏪 ПВЗ", callback_data="cat_pvz"))
    markup.add(types.InlineKeyboardButton("🔄 Возврат", callback_data="cat_return"))
    markup.add(types.InlineKeyboardButton("💰 Цена", callback_data="cat_price"))
    markup.add(types.InlineKeyboardButton("😍 Эмоции", callback_data="cat_emotion"))
    bot.send_message(message.chat.id, "📝 WB Templates (6 категорий):", reply_markup=markup)

# Templates callbacks
@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))
def templates_callback(call):
    data = call.data
    bot.answer_callback_query(call.id)
    
    templates = {
        'cat_size': "📏 '42-44 готово, FBO 3-5 дней'",
        'cat_delivery': "🚚 'WB курьер? СДЭК точка 124'",
        'cat_pvz': "🏪 'ПВЗ готов, код 1234'",
        'cat_return': "🔄 'Возврат одобрен, трек 123456789'",
        'cat_price': "💰 'Цена 1999₽, скидка 20%'",
        'cat_emotion': "😍 'Обожаю ваши отзывы! ❤️'"
    }
    bot.send_message(call.message.chat.id, templates.get(data, "📝 Шаблон готов!"))

# Track callbacks
@bot.callback_query_handler(func=lambda call: call.data.startswith('t_'))
def track_callback(call):
    _, order_id, status = call.data.split('_', 2)
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"💬 '{status}': Заказ #{order_id} в пути...")

@bot.callback_query_handler(func=lambda call: call.data in ['wb_link', 'review'])
def simple_callback(call):
    bot.answer_callback_query(call.id)
    if call.data == 'wb_link':
        bot.send_message(call.message.chat.id, "🔗 sellers.wildberries.ru")
    else:
        bot.send_message(call.message.chat.id, "⭐ Спасибо за 5⭐!")

# ================================
# 💰 /pay — Монетизация
# ================================
@bot.message_handler(commands=['pay'])
def pay_handler(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("💳 300₽ Pro (50+ шаблонов)", url="https://yoomoney.ru/to/41001750951472")
    markup.add(btn)
    bot.send_message(message.chat.id, "💰 TrackOrderPro Pro\n• 50+ шаблонов\n• NightGuard Pro\n• 300₽ разово", reply_markup=markup)

# ================================
# ЗАПУСК
# ================================
if __name__ == "__main__":
    print("✅ /start /track /templates /night /pay")
    print("📡 Polling...")
    bot.infinity_polling()
