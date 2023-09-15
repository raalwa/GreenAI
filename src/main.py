import csv
import logging
import shutil
import time
from datetime import datetime

import schedule
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import config

gauth = GoogleAuth()
drive = GoogleDrive()


def init():
    logging.basicConfig()
    schedule_logger = logging.getLogger('schedule')
    schedule_logger.setLevel(level=logging.DEBUG)
    setup_csv()


def setup_periodic_schedule():
    schedule.every(5).seconds.do(run)
    schedule.every(25).seconds.do(backup_csv)
    return schedule.CancelJob


def setup_csv():
    with open(f'{config.LOGS_PATH}/{config.LOG_FILENAME}', 'w', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=config.FIELDNAMES)
        writer.writeheader()


def append_data(row):
    with open(f'{config.LOGS_PATH}/{config.LOG_FILENAME}', 'a', encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=config.FIELDNAMES)
        writer.writerow(row)


def backup_csv():
    filename_backup = f'{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}_{config.LOG_FILENAME}'
    shutil.copy(f'{config.LOGS_PATH}/{config.LOG_FILENAME}',
                f'{config.LOGS_PATH}/{filename_backup}')
    google_drive_file = drive.CreateFile(
        {'parents': [{'id': config.FOLDER_ID}], 'title': f'{filename_backup}'})
    google_drive_file.SetContentFile(f'{config.LOGS_PATH}/{filename_backup}')
    google_drive_file.Upload()


def run():
    data = {'time': time.time()}
    print(f'Ran at {data}')
    append_data(data)


if __name__ == '__main__':
    init()
    schedule.every().day.at(config.STARTTIME).do(setup_periodic_schedule)
    while True:
        schedule.run_pending()
        time.sleep(1)
