import requests
import random


def send_request(bot, my_chat_id: int, message) -> None:
    """
        Відправляє повідомлення з новою заявкою.

        Parameters:
            bot (Bot): Екземпляр бота Telegram.
            my_chat_id (int): ID чату адміністратора.
            message (Message): Повідомлення з заявкою.

        Returns:
            None
        """
    for_me = f'Нова заявка: {message.text}'
    bot.send_message(my_chat_id, for_me)
    bot.send_message(message.chat.id, 'Дякую за заяву! Очікуйте лист на електронну адресу!')


def send_service(bot, message) -> None:
    """
    Відправляє повідомлення з переліком доступних послуг.

    Parameters:
        bot (Bot): Екземпляр бота Telegram.
        message (Message): Повідомлення для відправки послуг.

    Returns:
        None
    """
    bot.send_message(message.chat.id, '1. Замовити телеграм чат бота зі своїми вимогами: 1500 - 2500 UAH')
    bot.send_message(message.chat.id, '2. Замовити бекенд розробку для вашого сайту: 2300 - 3500 UAH')
    bot.send_message(message.chat.id, '3. Домовитись з розробником на кастомний проект: 1000 - 6000 UAH')


def send_bug(bot, my_chat_id: int, message) -> None:
    """
    Відправляє повідомлення про виявлений баг.

    Parameters:
        bot (Bot): Екземпляр бота Telegram.
        my_chat_id (int): ID чату адміністратора.
        message (Message): Повідомлення про виявлений баг.

    Returns:
        None
    """
    bug_user = f'Баг/Некоректна робота: {message.text}'
    bot.send_message(my_chat_id, bug_user)
    bot.send_message(message.chat.id, 'Дякую за допомогу в коректній роботі бота!')


def get_currency_rates(bot, message, currency_api_url, currencies_to_display) -> None:
    """
    Отримує та відображає актуальні курси валют.

    Parameters:
        bot (Bot): Екземпляр бота Telegram.
        message (Message): Повідомлення для відправки результатів.
        currency_api_url (str): URL API для отримання курсів валют.
        currencies_to_display (List[str]): Список валют, курси яких необхідно відобразити.

    Returns:
        None
    """
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


def play(bot, message, dices) -> None:
    """
    Гра у кидання кубика.

    Parameters:
        bot (Bot): Екземпляр бота Telegram.
        message (Message): Повідомлення для відправки результату гри.
        dices (List[str]): Список доступних кубиків для гри.

    Returns:
        None
    """
    new_dice = random.choice(dices)
    bot.send_dice(message.chat.id, new_dice)
