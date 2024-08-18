import telebot
from telebot import types
import sqlite3
import openai

# Вставьте ваш API-ключ OpenAI и токен Telegram бота
openai.api_key = 'sk-G_BVvS_32Akmf1XeBalsv8dUEVXxzF1V98svSq25pcT3BlbkFJ8F5OurR6rg_oIlosGn-064amPX0-6QdW-kjWRXjdUA'
bot = telebot.TeleBot("7388261265:AAFnEVEYSheetWFzoWbRYO1eVLn3I5x7avs")

# Имя файла базы данных
DB_FILE = "database.sql"

def initialize_db():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            username TEXT,
            birth_date TEXT,
            city TEXT,
            gender TEXT
        )
    """)
    connection.commit()
    connection.close()

@bot.message_handler(func=lambda message: message.text == '🌌 Мой знак зодиака')
def zodiac_signs(message):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("SELECT birth_date, city, gender FROM users WHERE user_id = ?", (message.from_user.id,))
    user_data = cursor.fetchone()
    connection.close()

    if user_data:
        birth_date, city, gender = user_data

        prompt = f"""
        Учитывая вашу дату рождения {birth_date}, город в котором вы родились {city} и пол {gender}, по Западному гороскопу вы:..., 
        по Китайскому вы:..., по Ведическому вы:..., по Майя вы:..., по Японскому вы:... без лишней информации и в столбик без изменений
        """

        zodiac_response = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )

        response_text = zodiac_response.choices[0].message['content']
        bot.send_message(message.chat.id, response_text)
    else:
        bot.send_message(message.chat.id, "Данные не найдены. Пожалуйста, введите их с помощью команды /start.")

@bot.message_handler(commands=['start'])
def start(message):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("SELECT birth_date, city, gender FROM users WHERE user_id = ?", (message.from_user.id,))
    user_data = cursor.fetchone()
    connection.close()

    if user_data:
        show_menu(message)
    else:
        bot.send_message(message.chat.id, "Укажи дату рождения в формате (день-месяц-год)")
        bot.register_next_step_handler(message, userdate)

def show_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('🔮 Гороскоп')
    btn2 = types.KeyboardButton('🤍 Совместимости')
    markup.row(btn1, btn2)
    btn3 = types.KeyboardButton('✒️ Цитаты')
    btn4 = types.KeyboardButton('💼 Работа')
    markup.row(btn3, btn4)
    btn5 = types.KeyboardButton('📂 Данные')
    markup.row(btn5)

    file = open('./Circle.jpg', 'rb')
    bot.send_photo(message.chat.id, file, reply_markup=markup)

    with open('./Main_Page.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    bot.send_message(message.chat.id, content, reply_markup=markup)

def userdate(message):
    numbers = message.text.strip()
    bot.send_message(message.chat.id, "Теперь укажи город.")
    bot.register_next_step_handler(message, lambda msg: usercity(msg, numbers))

def usercity(message, numbers):
    city = message.text.strip()
    bot.send_message(message.chat.id, "Теперь укажи ваш пол (мужской/женский).")
    bot.register_next_step_handler(message, lambda msg: usergender(msg, numbers, city))

def usergender(message, numbers, city):
    gender = message.text.strip().capitalize()
    if gender not in ["Мужской", "Женский"]:
        bot.send_message(message.chat.id, "Пожалуйста, укажите пол как 'мужской' или 'женский'.")
        bot.register_next_step_handler(message, lambda msg: usergender(msg, numbers, city))
        return
    save_to_db(message, numbers, city, gender)
    bot.send_message(message.chat.id, "Данные сохранены!")
    show_menu(message)

def save_to_db(message, birth_date, city, gender):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, username, birth_date, city, gender) VALUES (?, ?, ?, ?, ?)",
                   (message.from_user.id, message.from_user.username, birth_date, city, gender))
    connection.commit()
    connection.close()

@bot.message_handler(func=lambda message: message.text == '📂 Данные')
def show_user_data(message):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("SELECT birth_date, city, gender FROM users WHERE user_id = ?", (message.from_user.id,))
    user_data = cursor.fetchone()
    connection.close()

    if user_data:
        birth_date, city, gender = user_data
        bot.send_message(message.chat.id, f"Дата рождения: {birth_date}\nГород: {city}\nПол: {gender}")
    else:
        bot.send_message(message.chat.id, "Данные не найдены. Пожалуйста, введите их с помощью команды /start.")

@bot.message_handler(func=lambda message: message.text == '🔮 Гороскоп')
def choose_period(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('На Сегодня')
    btn2 = types.KeyboardButton('На Неделю')
    markup.row(btn1, btn2)
    btn3 = types.KeyboardButton('На Месяц')
    btn4 = types.KeyboardButton('На Год')
    markup.row(btn3, btn4)
    btn5 = types.KeyboardButton('🌌 Мой знак зодиака')
    markup.row(btn5)
    btn6 = types.KeyboardButton('◀️ Назад')
    markup.row(btn6)

    file = open('./Signs.jpg', 'rb')
    bot.send_photo(message.chat.id, file,'🔮 Гороскоп: Узнай свой персональный гороскоп на сегодня, чтобы быть в курсе, что звезды предсказывают для тебя.', reply_markup=markup)

    @bot.message_handler(func=lambda message: message.text == '◀️ Назад')
    def go_back(message):
        show_menu(message)




@bot.message_handler(func=lambda message: message.text in ['На Сегодня', 'На Неделю', 'На Месяц', 'На Год'])
def send_horoscope(message):
    period_map = {
        'На Сегодня': 'today',
        'На Неделю': 'week',
        'На Месяц': 'month',
        'На Год': 'year'
    }

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("SELECT birth_date, city, gender FROM users WHERE user_id = ?", (message.from_user.id,))
    user_data = cursor.fetchone()
    connection.close()

    if user_data:
        birth_date, city, gender = user_data
        prompt = f"""
        Учитывая вашу дату рождения {birth_date}, город в котором вы родились {city} и пол {gender},
        ваше предсказание выглядит так:
        Объедини Западный, Китайский, Ведический, Майя и Японский гороскоп и сделай единое не большое законченое предсказание на {period_map[message.text]} не указывая какой гороскоп.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        bot.send_message(message.chat.id, response.choices[0].message['content'].strip())
    else:
        bot.send_message(message.chat.id, "Данные не найдены. Пожалуйста, введите их с помощью команды /start.")

@bot.message_handler(func=lambda message: message.text == '✒️ Цитаты')
def send_quotes(message):
    quotes_response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=[{"role": "user", "content": "Напиши краткую умную цитату."}],
        temperature=0.7,
        max_tokens=150,
        frequency_penalty=0,
        presence_penalty=0
    )
    quote = quotes_response.choices[0].message['content']
    bot.send_message(message.chat.id, quote)

@bot.message_handler(func=lambda message: message.text == '🤍 Совместимости')
def compatibility(message):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("SELECT birth_date, city, gender FROM users WHERE user_id = ?", (message.from_user.id,))
    user_data = cursor.fetchone()
    connection.close()

    if user_data:
        birth_date, city, gender = user_data

        prompt = f"""
        Учитывая вашу дату рождения {birth_date}, город в котором вы родились {city} и пол {gender}, вам подайдет такой пратнер (Предоставь знак зодиака по Западному, Китайскому, Ведическому)вот почему (предоставь краткие причины почему этот партнер подходящий)
        """

        compatibility_response = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.7
        )

        response_text = compatibility_response.choices[0].message['content']
        bot.send_message(message.chat.id, response_text)
    else:
        bot.send_message(message.chat.id, "Данные не найдены. Пожалуйста, введите их с помощью команды /start.")

@bot.message_handler(func=lambda message: message.text == '💼 Работа')
def job_suggestion(message):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("SELECT birth_date, city, gender FROM users WHERE user_id = ?", (message.from_user.id,))
    user_data = cursor.fetchone()
    connection.close()

    if user_data:
        birth_date, city, gender = user_data

        prompt = f"""
        Учитывая вашу дату рождения {birth_date}, город в котором вы родились {city} и пол {gender}, Вам лучше всего подойдет эта профессия (напиши название профессии ) потому что (напиши причины)
        """

        job_response = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )

        response_text = job_response.choices[0].message['content']
        bot.send_message(message.chat.id, response_text)
    else:
        bot.send_message(message.chat.id, "Данные не найдены. Пожалуйста, введите их с помощью команды /start.")

initialize_db()
bot.polling()
