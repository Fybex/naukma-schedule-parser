from schedule_parser import parse_workbook_to_schedules
from save_schedule import clean_parsed_schedules_dir, save_schedule
from workbook_loader import load_workbook_from_url
from config import SCHEDULES_URLS

if __name__ == '__main__':
    clean_parsed_schedules_dir()

    schedules = {}

    for index, url in enumerate(SCHEDULES_URLS):
        workbook = load_workbook_from_url(url)
        schedules = {**schedules, **parse_workbook_to_schedules(workbook)}

    save_schedule(schedules, 'schedule')
