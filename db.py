import telebot
import sqlite3
import schedule
from telebot import types

from config import API_TOKEN

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['mood'])
def mood_answer(message):
    user_id = message.from_user.id
    answer = message.text

    conn = sqlite3.connect('moodbase.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, answer TEXT)')
    cur.execute('INSERT INTO users (id, answer) VALUES (?, ?)', (user_id, answer))
    conn.commit()
    cur.close()
    conn.close()

# def mood_question(message):
#     keyboard = types.InlineKeyboardMarkup()
#     key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
#     keyboard.add(key_yes)
#     key_no= types.InlineKeyboardButton(text='Нет', callback_data='no')
#     keyboard.add(key_no)
#     bot.send_message(message.chat.id, 'Как твоё настроение сегодня? Оцени своё настроение от -3 до +3.')

#     schedule.every().day.at("12:44").do(mood_question)

# @bot.callback_query_handler(func=lambda call: True)
# def callback_answer(call):
#     conn = sqlite3.connect('moodbase.sql')
#     cur = conn.cursor()
#     if call.data == "yes":
#         bot.send_message(call.message.chat.id, 'Записал.')
#     elif call.data == "no":
#         bot.send_message(call.message.chat.id, 'Как твоё настроение сегодня? Оцени своё настроение от -3 до +3.')



def main():
    conn = sqlite3.connect('moodbase.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, answer TEXT)')
    conn.commit()
    cur.close()
    conn.close()


# bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()

# просто кнопка
# @bot.message_handler(commands=['button'])
# def button_message(message):
#     markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
#     item1=types.KeyboardButton("Кнопка")
#     markup.add(item1)
#     bot.send_message(
#         message.chat.id,
#         'Выберите что вам надо',
#         reply_markup=markup)