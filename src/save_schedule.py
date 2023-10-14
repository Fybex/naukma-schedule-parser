import json
from dataclasses import is_dataclass, asdict

from constants import PARSED_SCHEDULES_DIR

__all__ = ['print_schedule', 'clean_parsed_schedules_dir', 'save_schedule']


class DataclassEncoder(json.JSONEncoder):
    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        elif hasattr(obj, 'value'):
            return obj.value
        return super().default(obj)


def get_json(schedule):
    return json.dumps(schedule, cls=DataclassEncoder, indent=4, ensure_ascii=False)


def print_schedule(schedule):
    """Print the schedule to the console."""
    print(get_json(schedule))


def clean_parsed_schedules_dir():
    """Remove all files from the parsed schedules directory."""
    import os
    import shutil

    if os.path.exists(PARSED_SCHEDULES_DIR):
        shutil.rmtree(PARSED_SCHEDULES_DIR)

    os.makedirs(PARSED_SCHEDULES_DIR)


def save_schedule(schedule, filename='schedule'):
    """Save the schedule to a JSON file."""
    with open(f'{PARSED_SCHEDULES_DIR}/{filename}.json', 'w') as file:
        file.write(get_json(schedule))
