import requests
import json


def get_weather(bot, message, API) -> None:
    """
    Отримує погоду для заданого міста.

    Parameters:
        bot (Bot): Екземпляр бота Telegram.
        message (Message): Повідомлення, що містить запит на погоду.
        API (str): Ключ API для openweathermap.org.

    Returns:
        None
    """
    bot.send_message(message.chat.id, 'Введіть назву міста для отримання погоди зараз, прошу вводити їх назви без помилок :D')
    bot.register_next_step_handler(message, lambda msg: process_weather_request(bot, msg, API))


def process_weather_request(bot, message, API) -> None:
    """
    Обробляє запит на погоду та відправляє результати користувачу.

    Parameters:
        bot (Bot): Екземпляр бота Telegram.
        message (Message): Повідомлення з назвою міста для запиту погоди.
        API (str): Ключ API для openweathermap.org.

    Returns:
        None
    """
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

        file = open(image, 'rb')
        bot.send_photo(message.chat.id, file)
    else:
        bot.reply_to(message, 'Місто вказано не вірно, або щось пішло не так.')
