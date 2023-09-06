import schedule, time
from bot import bot
from config import CHAT_ID

"""Запуск планировщика в основном потоке."""
if __name__ == '__main__':

    """Функция отправки уведомления."""
    def notification_message(chatid):
        bot.send_message(chatid, text='Как ты сегодня?')

    schedule.every().day.at("17:34").do(notification_message, chatid=CHAT_ID)

    while True:
        schedule.run_pending()
        time.sleep(1)
