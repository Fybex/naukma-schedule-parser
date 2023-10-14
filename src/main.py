import os

from schedule_parser import parse_workbook_to_schedules
from save_schedule import save_schedule
from workbook_loader import get_workbook_sources, load_workbook_from_source

if __name__ == '__main__':
    schedules = {}

    sources = get_workbook_sources()
    for index, source in enumerate(sources):
        print(f"Loading workbook ({index + 1}/{len(sources)}) from: {source}")
        workbook = load_workbook_from_source(source)
        print(f"Processing workbook ({index + 1}/{len(sources)})...")
        schedules = {**schedules, **parse_workbook_to_schedules(workbook)}

    print("Saving schedule...")
    save_schedule(schedules, 'schedule')
    print(f"Schedule saved to: {os.path.abspath('data/schedule.json')}")
