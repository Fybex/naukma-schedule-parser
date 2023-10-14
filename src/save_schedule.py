import json
import os
from dataclasses import is_dataclass, asdict

from config import PARSED_SCHEDULE_DIR

__all__ = ['print_schedule', 'save_schedule']


class DataclassEncoder(json.JSONEncoder):
    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        elif hasattr(obj, 'value'):
            return obj.value
        return super().default(obj)


def serialize_schedule_to_json(schedule):
    """Serialize the schedule into JSON format."""
    return json.dumps(schedule, cls=DataclassEncoder, indent=4, ensure_ascii=False)


def print_schedule(schedule):
    """Print the schedule to the console."""
    print(serialize_schedule_to_json(schedule))


def remove_files_in_directory(directory: str):
    """Delete all files in the specified directory."""
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


def save_schedule(schedule, filename='schedule'):
    """Save the schedule to a JSON file."""
    os.makedirs(PARSED_SCHEDULE_DIR, exist_ok=True)
    with open(os.path.join(PARSED_SCHEDULE_DIR, f"{filename}.json"), 'w') as file:
        file.write(serialize_schedule_to_json(schedule))
