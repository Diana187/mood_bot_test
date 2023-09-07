import telebot
import sqlite3
from telebot import types


from config import API_TOKEN

bot = telebot.TeleBot(API_TOKEN)

"""Создаём соединение и курсор."""
conn = sqlite3.connect('moodbase.sql')
cur = conn.cursor()

"""Создаём таблицу 'moodbase.sql' с полями id, response, если она ещё не существует."""
cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, response TEXT)')

conn.commit()
cur.close()
conn.close()

"""Функция обработки команды start."""
@bot.message_handler(commands=['start'])
def start(message):
    mess = f'Привет, {message.from_user.first_name}! Я бот-трекер настроения.'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Привет!")
    btn2 = types.KeyboardButton("Настроение")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, mess, reply_markup=markup)

    conn = sqlite3.connect('moodbase.sql')
    cur = conn.cursor()

    response = message.text
    user_id = message.chat.id

    """Создаём соединение и курсор."""
    cur.execute('INSERT INTO users (id, response) VALUES (?, ?)', (user_id, response,))

    conn.commit()
    cur.close()
    conn.close()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Посмотреть моё настроение.', callback_data='mood'))
    bot.send_message(message.chat.id, 'Записал твоё настроение.', reply_markup=markup)


"""Обработка текстовых сообщений."""
@bot.message_handler(content_types=['text'])
def get_user_messages(message):   
    if message.text == '👋 Привет!':
        bot.send_message(
            message.chat.id,
            'Приятно познакомиться. Я помогу следить за твоим самочувствием)'
        )
    elif message.text == 'Настроение':
        mess = f'{message.from_user.first_name}! Как твоё настроение сегодня?'
        markup = types.InlineKeyboardMarkup(row_width=3)
        item1 = types.InlineKeyboardButton("Хорошо", callback_data='good')
        item2 = types.InlineKeyboardButton("Нормально", callback_data='normal')
        item3 = types.InlineKeyboardButton("Плохо", callback_data='bad')
        markup.add(item1, item2, item3)
        bot.send_message(message.chat.id, mess, reply_markup=markup)
    else: 
        bot.send_message(
            message.chat.id,
            'Я тебя не понимаю('
        )

"""Обработка callback-запросов."""
@bot.callback_query_handler(func=lambda call:True)
def callbeck_inline_mood(call):
    try:
        if call.message:
            if call.data == 'good':
                bot.send_message(call.message.chat.id, 'Это замечательно!')
            elif call.data == 'normal':
                bot.send_message(call.message.chat.id, 'Хорошо, что всё нормально!')
            elif call.data == 'bad':
                bot.send_message(call.message.chat.id, 'Мне очень жаль(')
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                text='Я напомню тебе, когда придёт время отметить настроение.')
    except Exception as error:
        print(repr(error))

"""Запуск в основном потоке."""
if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
