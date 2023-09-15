import logging
import time

import schedule


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
    pass


def append_data():
    pass


def backup_csv():
    pass


def run():
    data = {'time': time.time()}
    print(f'Ran at {data}')


if __name__ == '__main__':
    init()
    schedule.every().day.at('19:10:30').do(setup_periodic_schedule)
    while True:
        schedule.run_pending()
        time.sleep(1)
