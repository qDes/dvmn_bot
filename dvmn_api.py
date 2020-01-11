import telegram
import requests
import os

from datetime import datetime
from dotenv import load_dotenv
from math import ceil
from requests.exceptions import ConnectionError, ReadTimeout
from time import sleep


def get_midnight_timestamp():
    now = datetime.now()
    today_midnight = datetime(now.year,
                              now.month,
                              now.day,
                              0, 0, 0, 0)
    midnight_timestamp = datetime.timestamp(today_midnight)
    return midnight_timestamp


def get_reviews(dvmn_token, timestamp):
    dvmn_url = "https://dvmn.org/api/long_polling/"
    payload = {"timestamp": timestamp}
    headers = {"Authorization": f"Token {dvmn_token}"}
    response = requests.get(dvmn_url, headers=headers,
                            params=payload, timeout=60)
    response.raise_for_status()
    return response.json()


def get_saved_timestamp():
    try:
        with open("timestamp", 'r') as f:
            timestamp = int(f.read())
    except (FileNotFoundError, ValueError):
        timestamp = get_midnight_timestamp()
    return timestamp


def save_timestamp(timestamp):
    with open("timestamp", 'w') as f:
        f.write(str(timestamp))


def create_message(attempt):
    lesson_title = attempt.get('lesson_title')
    is_negative = attempt.get('is_negative')
    result = "Работа принята."
    if is_negative:
        result = "В работе найдены ошибки. Исправьте их."
    message = f"""Урок {lesson_title} проверен.
                    
{result}
               """
    return message


def main():
    load_dotenv()
    dvmn_token = os.environ['DVMN_TOKEN']
    tg_token = os.environ['TG_TOKEN']
    chat_id = os.environ['TELEGRAM_CHAT_ID']
    timestamp = get_saved_timestamp()
    bot = telegram.Bot(token=tg_token)
    bot.send_message(chat_id=chat_id,
                     text="Start dvmn long polling.")
    while True:
        try:
            dvmn_resp = get_reviews(dvmn_token, timestamp)
            new_attempts = dvmn_resp.get('new_attempts')
            for attempt in new_attempts:
                message = create_message(attempt)
                timestamp = ceil(int(attempt.get('timestamp')))
                bot.send_message(chat_id=chat_id,
                                 text=message)
                sleep(1)
            timestamp += 1
            save_timestamp(timestamp)
        except ReadTimeout:
            pass
        except ConnectionError:
            pass


if __name__ == "__main__":
    main()
