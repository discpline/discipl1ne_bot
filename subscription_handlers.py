def subscribe(bot, cursor, conn, message):
    user_id = message.from_user.id
    cursor.execute('INSERT OR REPLACE INTO subscribers (user_id) VALUES (?);', (user_id,))
    conn.commit()
    bot.send_message(user_id, 'Ви підписані на отримання сповіщень!')

def unsubscribe(bot, cursor, conn, message):
    user_id = message.from_user.id
    cursor.execute('DELETE FROM subscribers WHERE user_id = ?;', (user_id,))
    conn.commit()
    bot.send_message(user_id, 'Ви відписались від отримання сповіщень.')
