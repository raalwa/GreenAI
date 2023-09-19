import csv
import logging
import shutil
import threading
import time
from datetime import datetime, timedelta, timezone
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
    get_API_token()


def run_threaded(func: Callable):
    # after https://schedule.readthedocs.io/en/stable/parallel-execution.html
    thread = threading.Thread(target=func)
    thread.start()


def setup_periodic_schedule():
    schedule.every(config.INTERVAL_MEASUREMENTS_MIN).minutes.do(
        run_threaded, run)
    schedule.every(config.INTERVAL_BACKUP_H).hours.do(run_threaded, backup_csv)
    return schedule.CancelJob


def get_API_token():
    print("Generating new token")
    global token
    try:
        with session.get(config.TOKEN_URL, auth=(config.USER, config.PASS)) as r:
            r.raise_for_status()
            token = r.json()['access_token']
    except Exception as exc:
        print('Exception:', exc)


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
    # for thread in threading.enumerate():
    #     print(thread.name)
    data = {}
    weather = get_weather()
    data['validdate'] = weather[0]['coordinates'][0]['dates'][0]['date']
    for value in weather:
        data[value['parameter']] = value['coordinates'][0]['dates'][0]['value']
    power = get_power()
    data.update(power)
    append_data(data)


def get_weather():
    global token
    validdate = f'{datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}'
    # print("Calling API with time:", validdate)
    try:
        with session.get(f'{config.API_URL}/{validdate}/{config.PARAMETERS}/{config.LOCATION}/{config.FORMAT}?access_token={token}') as r:
            r.raise_for_status()
            data = r.json()['data']
            return data
    except Exception as exc:
        print('Exception:', exc)


def get_power():
    data = {}
    data['current'] = ina260.current
    data['voltage'] = ina260.voltage
    data['power'] = ina260.power
    return data


if __name__ == '__main__':
    init()
    time_start = datetime.now() + timedelta(seconds=10)
    schedule.every().day.at(time_start.strftime("%H:%M:%S")).do(setup_periodic_schedule)
    schedule.every(110).minutes.do(run_threaded, get_API_token)
    while True:
        schedule.run_pending()
        time.sleep(1)
