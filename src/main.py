import csv
import logging
import shutil
import threading
import time
from datetime import datetime, timedelta
from typing import Callable

import adafruit_ina260
import board
import requests
import schedule
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import config

gauth = GoogleAuth()
drive = GoogleDrive()

token = ''
session = requests.Session()

i2c = board.I2C()
ina260 = adafruit_ina260.INA260(i2c)


def init():
    print("Start init")
    logging.basicConfig()
    schedule_logger = logging.getLogger('schedule')
    schedule_logger.setLevel(level=logging.DEBUG)
    setup_csv()


def run_threaded(func: Callable):
    # after https://schedule.readthedocs.io/en/stable/parallel-execution.html
    thread = threading.Thread(target=func)
    thread.start()


def setup_periodic_schedule():
    schedule.every(config.INTERVAL_MEASUREMENTS_MIN).minutes.do(
        run_threaded, run)
    schedule.every(config.INTERVAL_BACKUP_H).hours.do(run_threaded, backup_csv)
    return schedule.CancelJob


def setup_csv():
    with open(f'{config.LOGS_PATH}/{config.LOG_FILENAME}', 'w', encoding='UTF8', newline='') as file_csv:
        writer = csv.DictWriter(file_csv, fieldnames=config.FIELDNAMES)
        writer.writeheader()


def append_data(row):
    with open(f'{config.LOGS_PATH}/{config.LOG_FILENAME}', 'a', encoding='UTF8', newline='') as file_csv:
        writer = csv.DictWriter(file_csv, fieldnames=config.FIELDNAMES)
        writer.writerow(row)


def backup_csv():
    filename_backup = f'{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}_{config.LOG_FILENAME}'
    shutil.copy(f'{config.LOGS_PATH}/{config.LOG_FILENAME}',
                f'{config.LOGS_PATH}/{filename_backup}')
    google_drive_file = drive.CreateFile(
        {'parents': [{'id': config.GOOGLE_DRIVE_FOLDER_ID}], 'title': f'{filename_backup}'})
    google_drive_file.SetContentFile(f'{config.LOGS_PATH}/{filename_backup}')
    google_drive_file.Upload()


def run():
    data = {}
    weather = get_weather()
    for key in weather['current']:
        data[key] = weather['current'][key]
    data.pop('weather')
    power = get_power()
    data.update(power)
    append_data(data)
    return schedule.CancelJob


def get_weather():
    try:
        with session.get(f'{config.API_URL}lat={config.LATITUDE}&lon={config.LONGITUDE}&exclude={config.EXCLUDE}&appid={config.API_KEY}') as r:
            r.raise_for_status()
            data = r.json()
            return data
    except Exception as exc:
        print('Exception:', exc)


def get_power():
    data = {}
    current = ina260.current
    voltage = ina260.voltage
    power = current*voltage
    data['current'] = current
    data['voltage'] = voltage
    data['power'] = power
    return data


if __name__ == '__main__':
    init()
    time_start = datetime.now() + timedelta(seconds=10)
    schedule.every().day.at(time_start.strftime("%H:%M:%S")).do(setup_periodic_schedule)
    while True:
        schedule.run_pending()
        time.sleep(1)
