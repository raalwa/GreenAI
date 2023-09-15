import csv
import logging
import shutil
import time
from datetime import datetime

import schedule

import config


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
    shutil.copy(f'{config.LOGS_PATH}/{config.LOG_FILENAME}',
                f'{config.LOGS_PATH}/{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}_{config.LOG_FILENAME}')


def run():
    data = {'time': time.time()}
    print(f'Ran at {data}')
    append_data(data)


if __name__ == '__main__':
    init()
    schedule.every().day.at('19:25:10').do(setup_periodic_schedule)
    while True:
        schedule.run_pending()
        time.sleep(1)
