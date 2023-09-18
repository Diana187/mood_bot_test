import telebot
import sqlite3
from datetime import datetime
from telebot import types
import matplotlib.pyplot as plt
import numpy as np


from config import API_TOKEN

bot = telebot.TeleBot(API_TOKEN)

def setup_database():
    """Создаём соединение и курсор."""
    conn = sqlite3.connect('moodbase.sql')
    cur = conn.cursor()

    """Создаём таблицу 'moodbase.sql' с полями id, date, если она ещё не существует."""
    cur.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    cur.execute("""CREATE TABLE IF NOT EXISTS mood_responses
                (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id  INTEGER, date DATE, response TEXT)""")

    conn.commit()
    cur.close()
    conn.close()

"""Создание графика настроения при помощи библиотеки matplotlib."""
def mood_plot():
    x = np.arange(0, 10, 0.1)
    y = np.sin(x)

    plt.plot(x, y)
    plt.savefig('saved_figure.png')


"""Хендлер и функция для обработки команды /start"""
@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('moodbase.sql')
    cur = conn.cursor()

    user_id = message.chat.id

    """Создаём соединение и курсор."""
    cur.execute(f'SELECT * FROM users WHERE user_id={user_id}')
    users = cur.fetchall()

    if len(users) == 0:
        cur.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))

    conn.commit()
    cur.close()
    conn.close()

    """Создаём кнопки клавиатуры."""
    mess = f'Привет, {message.from_user.first_name}! Я бот-трекер настроения!'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Привет!")
    btn2 = types.KeyboardButton("Настроение")
    btn3 = types.KeyboardButton("Показать настроение")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, mess, reply_markup=markup)

"""Хендлер и функция для обработки нажатий кнопок."""
@bot.message_handler(content_types=['text'])
def get_user_messages(message):   
    if message.text == '👋 Привет!':
        bot.send_message(
            message.chat.id,
            'Приятно познакомиться. Я помогу следить за твоим самочувствием!'
        )
    elif message.text == 'Настроение':
        mess = f'{message.from_user.first_name}! Как твоё настроение сегодня?'
        markup = types.InlineKeyboardMarkup(row_width=3)
        item1 = types.InlineKeyboardButton("Хорошо", callback_data='good')
        item2 = types.InlineKeyboardButton("Нормально", callback_data='normal')
        item3 = types.InlineKeyboardButton("Плохо", callback_data='bad')
        markup.add(item1, item2, item3)
        bot.send_message(message.chat.id, mess, reply_markup=markup)
    elif message.text == 'Показать настроение':
        handle_show(message)
    else: 
        bot.send_message(
            message.chat.id,
            'Я тебя не понимаю('
        )

"""Обработка ответов на нажатие инлайн кнопок."""
def handle_mood(call):
    if call.data == 'good':
        bot.send_message(call.message.chat.id, 'Это замечательно!')
    elif call.data == 'normal':
        bot.send_message(call.message.chat.id, 'Хорошо, что всё нормально!')
    elif call.data == 'bad':
        bot.send_message(call.message.chat.id, 'Мне очень жаль.')
    
    conn = sqlite3.connect('moodbase.sql')
    cur = conn.cursor()

    user_id = call.message.chat.id
    response = call.data
    date = datetime.now()

    """Записываем ответы и дату ответа в базу данных."""
    cur.execute('INSERT INTO mood_responses (user_id, date, response) VALUES (?, ?, ?)', (user_id, date, response))

    conn.commit()
    cur.close()
    conn.close()

"""Обработка ответа на нажатие кнопки 'показать настроение'."""
def handle_show(message):
    bot.send_message(message.chat.id, 'Вот информация о твоём настроении:')

    conn = sqlite3.connect('moodbase.sql')
    cur = conn.cursor()

    user_id = message.chat.id

    """Достаём ответы из базы данных."""
    cur.execute(f'SELECT response, date FROM mood_responses WHERE user_id={user_id}')
    mood_rows = cur.fetchall()
    
    response_message = ''
    for row in mood_rows:
        mood_responses, dates = row[0], row[1]
        formated_dates = datetime.fromisoformat(dates).strftime('%d, %B %Y')
        response_message += f'{mood_responses}: {formated_dates}\n'
    
    bot.send_message(message.chat.id, response_message)

    cur.close()
    conn.close()

"""Обработка callback-запроса."""
@bot.callback_query_handler(func=lambda call:True)
def callback_inline(call):
    if call.data in ['good', 'normal', 'bad']:
        handle_mood(call)

"""Запуск в основном потоке."""
if __name__ == '__main__':
    setup_database()
    bot.polling(none_stop=True, interval=0)
