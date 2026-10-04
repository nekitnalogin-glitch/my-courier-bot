python
import telebot
from telebot import types
import sqlite3
import os

TOKEN = os.environ.get("8909829536:AAGb-ToUAwBGrL1rNwrdUHO9AE1LY_wEZdU", "123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ")
PARTNER_LINK = "https://trk.ppdu.ru/click?uid=350396&oid=2304&erid=CQH36pWzJqVGXC5oLP8WVVNCNqJmbhiUPijGiu4zpwPd7G&sub1=telegram_bot"
ADMIN_ID = 8202512654  # Твой ID цифрами

bot = telebot.TeleBot(TOKEN)

# --- ФУНКЦИЯ ДЛЯ БЕЗОПАСНОЙ РАБОТЫ С БАЗОЙ ---
def db_execute(query, params=()):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

# Создаем таблицу при запуске
db_execute('''CREATE TABLE IF NOT EXISTS users 
              (user_id INTEGER PRIMARY KEY, username TEXT, city TEXT)''')

# Список городов
ALLOWED_CITIES = ["москва", "санкт-петербург", "мск", "спб", "питер", "екатеринбург", "новосибирск", "казань", "нижний новгород", "челябинск", "самара", "омск", "ростов-на-дону", "уфа", "красноярск", "воронеж", "пермь", "волгоград"]

# --- ГЛАВНОЕ МЕНЮ ---
def get_main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🚀 Начать регистрацию", callback_data="start_reg")
    btn2 = types.InlineKeyboardButton("🆘 Поддержка", callback_data="support")
    btn3 = types.InlineKeyboardButton("ℹ️ О проекте", callback_data="about")
    markup.add(btn1, btn2, btn3)
    return markup

# --- КОМАНДА /start ---
@bot.message_handler(commands=['start'])
def start_message(message):
    # Сохраняем пользователя БЕЗОПАСНО
    db_execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", 
               (message.chat.id, message.from_user.username))
    
    bot.send_message(
        message.chat.id,
        "Привет! 👋 Я бот-помощник для курьеров Яндекс.Еды.\n\n"
        "Я помогу тебе быстро зарегистрироваться и начать зарабатывать.\n"
        "Выбери действие ниже:",
        reply_markup=get_main_menu()
    )

# --- ОБРАБОТКА КНОПОК ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "start_reg":
        bot.send_message(call.message.chat.id, "Отлично! Напиши название своего города (например: Москва).")
        bot.register_next_step_handler(call.message, check_city)
        
    elif call.data == "support":
        bot.send_message(call.message.chat.id, "Напиши свой вопрос, и я передам его оператору. Он ответит в ближайшее время.")
        bot.register_next_step_handler(call.message, send_to_support)
        
    elif call.data == "about":
        bot.send_message(call.message.chat.id, 
                         "Этот бот создан для помощи курьерам. Мы сотрудничаем с Яндекс.Едой и помогаем с быстрой регистрацией.\n\n"
                         "Нажми /start, чтобы вернуться в меню.")
        
    elif call.data == "back_to_menu":
        bot.edit_message_text("Главное меню:", call.message.chat.id, call.message.message_id, reply_markup=get_main_menu())

# --- ПРОВЕРКА ГОРОДА ---
def check_city(message):
    city = message.text.strip().lower()
    
    if city in ALLOWED_CITIES:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("👉 Пройти регистрацию", url=PARTNER_LINK)
        markup.add(btn)
        
        bot.send_message(
            message.chat.id,
            f"Отлично! В городе {message.text} есть вакансии. 🎉\n\n"
            "Нажми на кнопку ниже, чтобы заполнить анкету. Это займет 2 минуты:",
            reply_markup=markup
        )
        # Сохраняем город БЕЗОПАСНО
        db_execute("UPDATE users SET city = ? WHERE user_id = ?", (city, message.chat.id))
        
    else:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("🔄 Попробовать другой город", callback_data="start_reg")
        btn2 = types.InlineKeyboardButton("🆘 Поддержка", callback_data="support")
        markup.add(btn1, btn2)
        
        bot.send_message(
            message.chat.id,
            f"К сожалению, в городе {message.text} пока нет открытых вакансий. 😔\n\n"
            "Но мы постоянно расширяемся! Ты можешь попробовать другой город или написать в поддержку.",
            reply_markup=markup
        )

# --- ОТПРАВКА ВОПРОСА АДМИНУ ---
def send_to_support(message):
    if message.text:
        bot.send_message(
            ADMIN_ID, 
            f"🆘 ВОПРОС ОТ КУРЬЕРА!\n\n"
            f"ID: {message.chat.id}\n"
            f"Юзер: @{message.from_user.username}\n"
            f"Текст: {message.text}"
        )
        bot.send_message(
            message.chat.id, 
            "✅ Твой вопрос отправлен оператору. Ожидай ответа!",
            reply_markup=get_main_menu()
        )
    else:
        bot.send_message(message.chat.id, "Пожалуйста, напиши текстом.", reply_markup=get_main_menu())

# --- ЗАЩИТА ОТ ДУРАКА ---
@bot.message_handler(content_types=['text'])
def fallback_handler(message):
    bot.send_message(
        message.chat.id,
        "Я тебя не совсем понял. 🤔\n"
        "Пожалуйста, используй кнопки меню или напиши /start.",
        reply_markup=get_main_menu()
    )

# --- ЗАПУСК ---
print("Бот запущен и работает...")
bot.polling(none_stop=True)