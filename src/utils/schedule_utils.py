import re
from typing import Tuple, List

from schedule_types import DayOfWeek, PairType, TimeSlot
from .string_utils import clean_cell_value, calculate_levenshtein_distance


def detect_day(cell_value: str) -> DayOfWeek | None:
    """Identify if the cell value corresponds to a day of the week. If so, return it; otherwise, return None."""
    if not cell_value:
        return None

    refined_cell_value = clean_cell_value(cell_value)
    threshold = 1  # Allow a maximum of one typo

    for day in DayOfWeek:
        if (
            calculate_levenshtein_distance(refined_cell_value, day.value.lower())
            <= threshold
        ):
            return day

    return None


def determine_lesson_type_and_group(lesson: str | int) -> Tuple[PairType, int | None]:
    """Distinguish the type of lesson (lecture or practical) and ascertain the group number (if applicable)."""
    # Convert all inputs to string for easier processing
    lesson_str = str(lesson).strip().lower()

    if PairType.LECTURE.value.lower() in lesson_str.lower():
        return PairType.LECTURE, None

    if lesson_str[0].isdigit():
        group_number = int(''.join(filter(str.isdigit, lesson_str)))
        return PairType.PRACTICE, group_number

    return PairType.UNKNOWN, None


def convert_to_time(time_interval: str) -> TimeSlot:
    """
    Convert the time interval string into a structured format.

    Example: "9:30-11:05" -> { "start": "9:30", "end": "11:05" }
    """
    start, end = map(lambda x: x.strip(), time_interval.split("-"))
    return TimeSlot(start, end)


def extract_weeks(weeks: str) -> List[int]:
    """
    Convert the weeks string into a list of integer week numbers.

    Example: "1-3, 5, 7-9" -> [1, 2, 3, 5, 7, 8, 9]
    """
    weeks_list = [week.strip() for week in weeks.split(",")]
    result = []

    for week in weeks_list:
        if "-" in week:
            start_week, end_week = map(int, week.split("-"))
            result.extend(range(start_week, end_week + 1))
        else:
            result.append(int(week))

    return result


def fetch_specialities(speciality_val: str | None) -> List[str]:
    """Retrieve all specialties from the provided string."""
    if not speciality_val:
        return []

    specialities = re.findall(r'«([^»]*)»', speciality_val) + re.findall(
        r'"([^"]*)"', speciality_val
    )
    return [speciality.strip() for speciality in specialities]
