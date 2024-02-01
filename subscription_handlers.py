import sqlite3

from app import bot

conn = sqlite3.connect('users.db', check_same_thread=False)
conn_2 = sqlite3.connect('subscribers.db', check_same_thread=False)
cursor_2 = conn.cursor()
cursor_2.execute('CREATE TABLE IF NOT EXISTS subscribers (user_id INTEGER PRIMARY KEY);')
conn_2.commit()


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