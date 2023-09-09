import telebot
import sqlite3
from telebot import types


from config import API_TOKEN

bot = telebot.TeleBot(API_TOKEN)

def setup_database():
    """Создаём соединение и курсор."""
    conn = sqlite3.connect('moodbase.sql')
    cur = conn.cursor()

    """Создаём таблицу 'moodbase.sql' с полями id, если она ещё не существует."""
    cur.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    cur.execute("""CREATE TABLE IF NOT EXISTS mood_responses
                (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id  INTEGER, response TEXT)""")
    

    conn.commit()
    cur.close()
    conn.close()

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
        bot.send_message(message.chat.id, 'Вот информация о твоём настроении:')
    else: 
        bot.send_message(
            message.chat.id,
            'Я тебя не понимаю('
        )

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

    cur.execute('INSERT INTO mood_responses (user_id, response) VALUES (?, ?)', (user_id, response))

    cur.close()
    conn.close()

def handle_show():
    print('lala')

"""Обработка callback-запросов."""
@bot.callback_query_handler(func=lambda call:True)
def callback_inline(call):
    if call.data in ['good', 'normal', 'bad']:
        handle_mood(call)
    elif call.data == 'show':
        print(call.data)
        handle_show(call)


"""Запуск в основном потоке."""
if __name__ == '__main__':
    setup_database()
    bot.polling(none_stop=True, interval=0)
