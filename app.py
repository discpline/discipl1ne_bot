from flask import Flask, request
import sqlite3
import telebot
import wikipedia
import warnings
from dotenv import load_dotenv
import os
from subscription_handlers import subscribe, unsubscribe
from notification_handlers import send_notification
from weather_handlers import get_weather
from cat_handlers import cats
from service_handlers import send_request, send_service, send_bug, get_currency_rates, play



dices = ['🎲', '🎯', '🎰']
subscribed_users = {}

warnings.simplefilter("ignore", category=UserWarning)


currency_api_url = os.environ.get('currency_api_url')


currencies_to_display = ['EUR', 'GBP', 'JPY', 'UAH', 'RUB']

load_dotenv()
TOKEN = os.environ.get('TOKEN')
load_dotenv()
my_chat_id = os.environ.get('my_chat_id')


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
API = os.environ.get('API')
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
def handle_subscribe(message) -> None:
    """
    Обробляє команду підписки користувача на отримання сповіщень.

    Parameters:
        message (Message): Повідомлення від користувача.

    Returns:
        None
    """
    subscribe(bot, cursor_2, conn_2, message)


@bot.message_handler(commands=['unsubscribe'])
def handle_unsubscribe(message) -> None:
    """
    Обробляє команду відписки користувача від отримання сповіщень.

    Parameters:
        message (Message): Повідомлення від користувача.

    Returns:
        None
    """
    unsubscribe(bot, cursor_2, conn_2, message)


@bot.message_handler(commands=['send_notification'])
def handle_send_notification(message) -> None:
    """
    Обробляє команду відправки сповіщення підписникам.

    Parameters:
        message (Message): Повідомлення від адміністратора.

    Returns:
        None
    """
    send_notification(bot, cursor_2, my_chat_id, message)


@bot.message_handler(commands=['cats'])
def show_cats(message) -> None:
    """
    Обробляє команду відправки випадкового зображення кота.

    Parameters:
        message (Message): Повідомлення від користувача.

    Returns:
        None
    """
    cat_random = cats()  # Отримайте випадкове фото кота
    bot.send_message(message.chat.id, 'Всім подобаються котики, і ось випадкові зображення котиків, якими '
                                      'я володію, просто подивіться та розслабтеся.')
    with open(cat_random, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)


@bot.message_handler(commands=['weather'])
def handle_weather(message) -> None:
    """
    Обробляє команду для отримання погоди.

    Parameters:
        message (Message): Повідомлення від користувача.

    Returns:
        None
    """
    get_weather(bot, message, API)


@bot.message_handler(commands=['wiki'])
def wiki(message) -> None:
    """
    Обробляє команду для пошуку інформації у Вікіпедії.

    Parameters:
        message (Message): Повідомлення від користувача.

    Returns:
        None
    """
    bot.send_message(message.chat.id, 'Введіть ваш запит для пошуку у вікіпедії.')
    bot.register_next_step_handler(message, process_wiki_request)


def process_wiki_request(message) -> None:
    """
    Обробляє запит користувача та відправляє результати пошуку.

    Parameters:
        message (Message): Повідомлення від користувача.

    Returns:
        None
    """
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
def start_register(message) -> None:
    """
    Обробляє команду для початку реєстрації користувача.

    Parameters:
        message (Message): Повідомлення від користувача.

    Returns:
        None
    """
    #user_id = message.from_user.id

    bot.send_message(message.chat.id, 'Для регістрації введіть свій номер телефону (в форматі +1234567890):')
    bot.register_next_step_handler(message, process_phone_input)


def process_phone_input(message) -> None:
    """
    Обробляє введений користувачем номер телефону для реєстрації.

    Parameters:
        message (Message): Повідомлення від користувача з номером телефону.

    Returns:
        None
    """
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
def list_users(message) -> None:
    """
    Обробляє команду для виведення списку зареєстрованих користувачів.

    Parameters:
        message (Message): Повідомлення від адміністратора.

    Returns:
        None
    """
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    if message.chat.id == my_chat_id:
        if users:
            user_list = "\n".join([f"{user[0]}. {user[2]} (ID: {user[1]}, Phone: {user[3] if len(user) > 3 else 'Немає'})" for user in users])
            bot.send_message(message.chat.id, f"Список зареєстрованих користувачів:\n{user_list}")
        else:
            bot.send_message(message.chat.id, 'Немає зареєстрованих користувачів.')


@bot.message_handler(content_types=['text'])
def repeat_on_message(message) -> None:
    """
    Повторює повідомлення користувача або відповідає на команди.
    В нашому випадку виконує команди в залежності від повідомлення користувача.

    Parameters:
        message (Message): Повідомлення від користувача.

    Returns:
        None
    """
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
        bot.register_next_step_handler(message, lambda msg: send_request(bot, my_chat_id, msg))

    if message.text.lower() == 'список послуг':
        send_service(bot, message)

    if message.text.lower() == 'вказати на баг':
        bot.send_message(message.chat.id, 'Ви знайшли якийсь баг чи некоректну роботу? Напишіть будь ласка, '
                                          'що і де працює некоректно, ми все виправимо!')
        bot.register_next_step_handler(message, lambda msg: send_bug(bot, my_chat_id, msg))

    if message.text.lower() == 'курс валют':
        get_currency_rates(bot, message, currency_api_url, currencies_to_display)

    if message.text.lower() == 'зіграти в рандом':
        play(bot, message, dices)


@app.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'Test Bot', 200


@app.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://bot-discipline-f7313fe78025.herokuapp.com/' + TOKEN)
    return 'Test Bot', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
