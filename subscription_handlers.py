from app import cursor_2, conn, bot, conn_2


def subscribe(message):
    user_id = message.from_user.id
    cursor_2.execute('INSERT OR REPLACE INTO subscribers (user_id) VALUES (?);', (user_id,))
    conn.commit()
    bot.send_message(user_id, 'Ви підписані на отримання сповіщень!')


def unsubscribe(message):
    user_id = message.from_user.id
    cursor_2.execute('DELETE FROM subscribers WHERE user_id = ?;', (user_id,))
    conn_2.commit()
    bot.send_message(user_id, 'Ви відписались від отримання сповіщень.')