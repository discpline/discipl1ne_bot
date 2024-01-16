from flask import Flask, request
import sqlite3
import telebot
import base_functions
import requests
import json
import wikipedia
import requests
import random
import schedule
import threading
import time
import warnings
from dotenv import load_dotenv
import os


dices = ['🎲', '🎯', '🎰']
subscribed_users = {}

warnings.simplefilter("ignore", category=UserWarning)


currency_api_url = 'https://api.exchangerate-api.com/v4/latest/USD'


currencies_to_display = ['EUR', 'GBP', 'JPY', 'UAH', 'RUB']

load_dotenv()
TOKEN = os.environ.get('TOKEN')
load_dotenv()
my_chat_id = 718425574


conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

conn_2 = sqlite3.connect('subscribers.db', check_same_thread=False)
cursor_2 = conn.cursor()
cursor_2.execute('CREATE TABLE IF NOT EXISTS subscribers (user_id INTEGER PRIMARY KEY);')
conn_2.commit()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        username TEXT,
        phone_number TEXT DEFAULT NULL
    )
''')
conn.commit()

bot = telebot.TeleBot(TOKEN)
API = '3d9de74844d28377e81415151cbe6a66'
wikipedia.set_lang('uk')
app = Flask(__name__)


@bot.message_handler(commands=['start', ])
def basic_answer(message):
    bot.reply_to(message, 'Привіт, я телеграм бот, мій творець назвав мене Аква, рада з вами працювати.\n'
                          'Для того щоб дізнатися мої можливості введіть команду /help та гортайте вниз '
                          'щоб побачити їх всі, я можу виконувати справді '
                          'багато цікавих функцій, насолоджуйтеся, сподіваюся, що буду корисною для вас!!!\n'
                          'Для полегшення ось, що роблять не основні (розважальні) команди:\n'
                          '/weather - ви зможете дізнатися погоду у будь якому місті\n'
                          '/wiki - ви зможете скористатися вікіпедієї прямо звідси, зручно, чи не так?\n'
                          '/register - ви можете залишити свої данні, такі як телеграм ID, ваш нікнейм, '
                          'вони будуть залишені автоматично, та ввести свій номер телефону, щоб він '
                          'також був в базі данних\n'
                          '/cats - ви отримаєте зображення котиків, щоб розслабитись\n'
                          '/subscribe - Підписатись на сповіщення, які інколи буде надсилати адміністратор\n'
                          '/unsubscribe - Відписатись від сповіщень\n'
                          'Основні команди для того щоб залишити заяву та інші є кнопками, які стоять '
                          'над командами, що я показала вище, їх різниця в зовнішньому вигляді потрібна для того, щоб '
                          'зручно їх відрізняняти від неосновних та більш розважальних'
                          ' команд, які мають в себе на початку слеш(/).')


@bot.message_handler(commands=['help', ])
def handle_start(message):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton(text='Список послуг')
    btn2 = telebot.types.KeyboardButton(text='Посилання на розробника')
    btn3 = telebot.types.KeyboardButton(text='Залишити заяву')
    btn4 = telebot.types.KeyboardButton(text='Вказати на баг')
    btn_currency = telebot.types.KeyboardButton(text='Курс валют')
    btn5 = telebot.types.KeyboardButton(text='Зіграти в рандом')
    keyboard.add(btn1, btn2, btn3, btn4, btn_currency, btn5)
    keyboard.add(telebot.types.KeyboardButton('/subscribe'))
    keyboard.add(telebot.types.KeyboardButton('/unsubscribe'))
    keyboard.add(telebot.types.KeyboardButton('/cats'))
    keyboard.add(telebot.types.KeyboardButton('/weather'))
    keyboard.add(telebot.types.KeyboardButton('/wiki'))
    keyboard.add(telebot.types.KeyboardButton('/register'))
    bot.reply_to(message, 'Ось мої команди (їх можна '
                          'гортати вниз), для того щоб дізнатися, що вони роблять раджу ввести команду:\n '
                          '/start, там я повністю вам все розповіла:', reply_markup=keyboard)


@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    user_id = message.from_user.id
    cursor_2.execute('INSERT OR REPLACE INTO subscribers (user_id) VALUES (?);', (user_id,))
    conn.commit()
    bot.send_message(user_id, 'Ви підписані на отримання сповіщень!')


@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
    user_id = message.from_user.id
    cursor_2.execute('DELETE FROM subscribers WHERE user_id = ?;', (user_id,))
    conn_2.commit()
    bot.send_message(user_id, 'Ви відписались від отримання сповіщень.')


@bot.message_handler(commands=['send_notification'])
def send_notification(message):

    admin_id = my_chat_id
    if message.from_user.id == admin_id:
        bot.send_message(message.chat.id, 'Введіть текст сповіщення для підписників.')
        bot.register_next_step_handler(message, handle_notification_input)
    else:
        bot.send_message(message.chat.id, 'Ви не маєте прав для відправлення сповіщень.')



def handle_notification_input(message):
    notification_text = message.text
    cursor_2.execute('SELECT user_id FROM subscribers')
    subscribed_users = cursor_2.fetchall()

    for user_id in subscribed_users:
        bot.send_message(user_id[0], f'🔔 Адміністратор надіслав сповіщення! {notification_text}')
        print(f'Сповіщення надіслано користувачу {user_id[0]}.')

    bot.send_message(my_chat_id, 'Сповіщення відправлено підписникам.')
    print('Сповіщення надіслано всім підписникам.')



def cats():
    cat_list = ['1.jpg', '2.jpg', '3.jpg', '4.jpg']
    return random.choice(cat_list)


@bot.message_handler(commands=['cats'])
def show_cats(message):
    cat_random = cats()  # Отримайте випадкове фото кота
    bot.send_message(message.chat.id, 'Всім подобаються котики, і ось випадкові зображення котиків, якими '
                                      'я володію, просто подивіться та розслабтеся.')
    with open(cat_random, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)



@bot.message_handler(commands=['weather'])
def get_weather(message):
    bot.send_message(message.chat.id, 'Введіть назву міста для отримання погоди зараз, прошу вводити їх'
                                      ' назви без помилок :D')
    bot.register_next_step_handler(message, process_weather_request)


def process_weather_request(message):
    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    if res.status_code == 200:
        data = json.loads(res.text)
        temp = data["main"]["temp"]
        bot.reply_to(message, f'Зараз погода: {temp} градусів за цельсієм')

        if temp < 0.0:
            image = 'cold.png'
        elif 0.0 <= temp <= 14.0:
            image = 'clouds.png'
        else:
            image = 'sunny.png'

        file = open('./' + image, 'rb')
        bot.send_photo(message.chat.id, file)
    else:
        bot.reply_to(message, 'Місто вказано не вірно, або щось пішло не так.')


@bot.message_handler(commands=['wiki'])
def wiki(message):
    bot.send_message(message.chat.id, 'Введіть ваш запит для пошуку у вікіпедії.')
    bot.register_next_step_handler(message, process_wiki_request)



def process_wiki_request(message):
    query = message.text
    try:
        page = wikipedia.page(query)
        bot.send_message(message.chat.id, page.summary)
    except wikipedia.exceptions.DisambiguationError as e:
        options = ", ".join(e.options)
        bot.send_message(message.chat.id, f"Уточніть варіант. Можливі варіанти: {options}")
    except wikipedia.exceptions.PageError:
        bot.send_message(message.chat.id, "Нажаль, по вашому запиту нічого не знайдено.")
    except wikipedia.exceptions.HTTPTimeoutError:
        bot.send_message(message.chat.id, "На жаль, Вікіпедія недоступна в даний момент. Будь ласка, спробуйте пізніше.")
    except Exception as e:
        bot.send_message(message.chat.id, "Сталася помилка при обробці запиту. Будь ласка, спробуйте пізніше.")


@bot.message_handler(commands=['register'])
def start_register(message):
    #user_id = message.from_user.id

    bot.send_message(message.chat.id, 'Для регістрації введіть свій номер телефону (в форматі +1234567890):')
    bot.register_next_step_handler(message, process_phone_input)


def process_phone_input(message):
    user_id = message.from_user.id
    username = message.from_user.username
    phone_number = message.text


    cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        bot.send_message(message.chat.id, 'Ви вже зарегестровані.')
    else:

        cursor.execute('INSERT INTO users (user_id, username, phone_number) VALUES (?, ?, ?)',
                       (user_id, username, phone_number))
        conn.commit()
        bot.send_message(message.chat.id, 'Регістрація пройшла успішно!. Ваші данні збережені.')


@bot.message_handler(commands=['list_users'])
def list_users(message):
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    if message.chat.id == my_chat_id:
        if users:
            user_list = "\n".join([f"{user[0]}. {user[2]} (ID: {user[1]}, Phone: {user[3] if len(user) > 3 else 'Немає'})" for user in users])
            bot.send_message(message.chat.id, f"Список зареєстрованих користувачів:\n{user_list}")
        else:
            bot.send_message(message.chat.id, 'Немає зареєстрованих користувачів.')


def send_request(message):
    for_me = f'Нова заявка: {message.text}'
    bot.send_message(my_chat_id, for_me)
    bot.send_message(message.chat.id, 'Дякую за заяву! Очікуйте лист на електронну адресу!')


def send_service(message):
    bot.send_message(message.chat.id, '1. Замовити телеграм чат бота зі своїми вимогами: 1500 - 2500 UAH')
    bot.send_message(message.chat.id, '2. Замовити бекенд розробку для вашого сайту: 2300 - 3500 UAH')
    bot.send_message(message.chat.id, '3. Домовитись з розробником на кастомний проект: 1000 - 6000 UAH')


def send_bug(message):
    bug_user = f'Баг/Некоректна робота: {message.text}'
    bot.send_message(my_chat_id, bug_user)
    bot.send_message(message.chat.id, 'Дякую за допомогу в коректній роботі бота!')


def get_currency_rates(message):
    try:
        response = requests.get(currency_api_url)
        data = response.json()

        if 'rates' in data:
            rates = {currency: data['rates'][currency] for currency in currencies_to_display}
            rates_text = '\n'.join([f'{currency}: {rate}' for currency, rate in rates.items()])
            bot.reply_to(message, f'Актуальні курси валют до доллару:\n{rates_text}')
        else:
            bot.reply_to(message, 'Не вдалося отримати актуальні курси валют.')

    except Exception as e:
        print(e)
        bot.reply_to(message, 'Сталася помилка при обробці запиту. Спробуйте ще раз пізніше.')


def play(message):
    new_dice = random.choice(dices)
    bot.send_dice(message.chat.id, new_dice)


@bot.message_handler(content_types=['text'])
def repeat_on_message(message):
    if message.text.lower() == 'посилання на розробника':
        keyboard = telebot.types.InlineKeyboardMarkup()
        url_button = telebot.types.InlineKeyboardButton(text='Посилання на інстаграм розробника',
                                                        url='https://www.instagram.com/_.d1scipl1ne._/')
        url_button1 = telebot.types.InlineKeyboardButton(text='Посилання на сайт, який розробник зробив для диплому',
                                                              url='https://django-oneschool-29bda5f1f04f.herokuapp.com/')
        keyboard.add(url_button)
        keyboard.add(url_button1)
        bot.send_message(message.chat.id, 'Все що цікавить та пропозиції надсилайте в особисті '
                                          'повідомлення.', reply_markup=keyboard)
    if message.text.lower() == 'залишити заяву':
        bot.send_message(message.chat.id, 'Рада вас обслуговувати, вкажіть свою пошту та ініціали, по яким до'
                                          'вас можна звернутися! А також, що ви бажаєте замовити.')
        bot.register_next_step_handler(message, send_request)

    if message.text.lower() == 'список послуг':
        send_service(message)

    if message.text.lower() == 'вказати на баг':
        bot.send_message(message.chat.id, 'Ви знайшли якийсь баг чи некоректну роботу? Напишіть будь ласка, '
                                          'що і де працює некоректно, ми все виправимо!')
        bot.register_next_step_handler(message, send_bug)

    if message.text.lower() == 'курс валют':
        get_currency_rates(message)

    if message.text.lower() == 'зіграти в рандом':
        play(message)



@app.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'Test Bot', 200


@app.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://december-discipl1ne-bot-0c7124aec2d9.herokuapp.com/' + TOKEN)
    return 'Test Bot', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
