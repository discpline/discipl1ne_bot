def send_notification(bot, cursor, my_chat_id, message):
    admin_id = my_chat_id
    if message.from_user.id == admin_id:
        bot.send_message(message.chat.id, 'Введіть текст сповіщення для підписників.')
        bot.register_next_step_handler(message, lambda msg: handle_notification_input(bot, cursor, my_chat_id, msg))
    else:
        bot.send_message(message.chat.id, 'Ви не маєте прав для відправлення сповіщень.')

def handle_notification_input(bot, cursor, my_chat_id, message):
    notification_text = message.text
    cursor.execute('SELECT user_id FROM subscribers')
    subscribed_users = cursor.fetchall()

    for user_id in subscribed_users:
        bot.send_message(user_id[0], f'🔔 Адміністратор надіслав сповіщення! {notification_text}')
        print(f'Сповіщення надіслано користувачу {user_id[0]}.')

    bot.send_message(my_chat_id, 'Сповіщення відправлено підписникам.')
    print('Сповіщення надіслано всім підписникам.')
