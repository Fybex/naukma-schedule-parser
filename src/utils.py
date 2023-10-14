import re
from typing import List, Tuple

from schedule_types import DayOfWeek, PairType, TimeSlot


def is_keyword_present(content: str, keyword: str) -> bool:
    """Check if the keyword is a separate word in the content."""
    return re.search(r'\b' + re.escape(keyword) + r'\b', content, re.IGNORECASE) is not None


def get_specialities(speciality_val: str) -> List[str]:
    """Extract all specialities from the given string."""
    if not speciality_val:
        return []

    specialities = re.findall(r'«([^»]*)»', speciality_val) + re.findall(r'"([^"]*)"', speciality_val)
    return [speciality.strip() for speciality in specialities]


def levenshtein_distance(s1: str, s2: str) -> int:
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2 + 1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def normalize_cell_value(cell_value: str) -> str:
    """Normalize the cell value by removing all extra spaces and newlines."""
    return re.sub(r'\s+', ' ', cell_value).strip().replace("’", "'")


def identify_current_day(cell_value: str) -> DayOfWeek | None:
    """Check if the cell value represents a day and return it. Otherwise, return None."""
    if not cell_value:
        return None

    normalized_cell_value = normalize_cell_value(cell_value)
    threshold = 1  # Allow at most one typo

    for day in DayOfWeek:
        if levenshtein_distance(normalized_cell_value, day.value.lower()) <= threshold:
            return day

    return None


def identify_pair_type_and_group(pair: str | int) -> Tuple[PairType, int | None]:
    """Identify the type of the pair (lecture or practice) and the group number (if it exists)."""
    # Convert everything to string for easy processing
    pair_str = str(pair).strip().lower()

    if PairType.LECTURE.value.lower() in pair_str.lower():
        return PairType.LECTURE, None

    if pair_str[0].isdigit():
        group_number = int(''.join(filter(str.isdigit, pair_str)))
        return PairType.PRACTICE, group_number

    return PairType.UNKNOWN, None


def parse_time(time_slot: str) -> TimeSlot:
    """
    Parse the time slot string into a tuple of integers.

    Example: "9:30-11:05" -> { "start": "9:30", "end": "11:05" }
    """
    start_time, end_time = map(lambda x: x.strip(), time_slot.split("-"))
    return TimeSlot(start_time, end_time)


def parse_weeks(weeks: str) -> [int]:
    """
    Parse the weeks string into a list of integers.

    Example: "1-3, 5, 7-9" -> [1, 2, 3, 5, 7, 8, 9]
    """
    weeks = weeks.split(",")
    result = []

    for week in weeks:
        if "-" in week:
            start_week, end_week = map(lambda x: int(x), week.split("-"))
            result.extend(range(start_week, end_week + 1))
        else:
            result.append(int(week))

    return result
