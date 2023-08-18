import telebot
from telebot import types
import schedule, time
import threading

from config import API_TOKEN

bot = telebot.TeleBot(API_TOKEN)

"""Обработка входящего сообщения start."""
@bot.message_handler(commands=['start'])
def start(message):
    mess = f'Привет, {message.from_user.first_name}! Я бот-трекер настроения.'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Привет!")
    btn2 = types.KeyboardButton("Настроение")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, mess, reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_user_messages(message):
    if message.text == '👋 Привет!':
        bot.send_message(
            message.chat.id,
            'Приятно познакомиться. Я помогу тебе следить за настроением)'
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
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="😊 Как дела?",
            reply_markup=None)

            bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                text='Я напомню тебе, когда придёт время отметить настроение.')
    except Exception as error:
        print(repr(error))


def notification_message():
    print('Как ты сегодня?')

# schedule.every().day.at("11:35").do(notification_message)

# @bot.message_handler(func=lambda message: message.text == 'Настроение')
# def notification_message(message):
    # pass


# def scheduled_notification():
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

if __name__ == '__main__':
    schedule.every().day.at("11:45").do(notification_message)

#     notification_thread = threading.Thread(target=scheduled_notification)
#     notification_thread.start()
    
    bot.polling(none_stop=True, interval=0)
