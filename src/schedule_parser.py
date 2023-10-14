import re
from openpyxl import Workbook
from typing import List, Dict, Tuple

from utils import identify_current_day, identify_pair_type_and_group, parse_time, parse_weeks, is_keyword_present, \
    get_specialities
from schedule_types import Schedule, ScheduleItem, Lesson
from constants import TEACHER_TITLES

__all__ = [
    "parse_schedules_from_workbook"
]


def get_headers_from_sheet(sheet) -> tuple:
    """Extract headers from the Excel sheet."""
    # Keywords.
    faculty_keyword = "факультет"
    speciality_keyword = "спеціальність"
    semester_keyword = "семестр"

    faculty_val = None
    speciality_val = None
    semester_val = None

    for row in sheet.iter_rows(values_only=True):
        for cell in row:
            if cell:
                if identify_current_day(cell):
                    return faculty_val, get_specialities(speciality_val), semester_val

                cell_content_lower = cell.lower()

                if is_keyword_present(cell_content_lower, faculty_keyword):
                    faculty_val = cell
                elif is_keyword_present(cell_content_lower, speciality_keyword):
                    speciality_val = cell
                elif is_keyword_present(cell_content_lower, semester_keyword):
                    semester_val = cell

    return faculty_val, get_specialities(speciality_val), semester_val


def merge_schedule_items(existing_item: ScheduleItem, new_item: ScheduleItem) -> ScheduleItem:
    """Merge two schedule items into one."""
    combined_weeks = list(set(existing_item.weeks + new_item.weeks))
    combined_weeks.sort()
    return ScheduleItem(
        type=existing_item.type,
        group=existing_item.group,
        time=existing_item.time,
        weeks=combined_weeks,
        location=existing_item.location,
        day=existing_item.day,
        teachers=existing_item.teachers
    )


def extract_subject_and_specialities(raw_subject_name: str, all_specialities: List[str]) -> Tuple[str, List[str]]:
    """Extract the subject name and the specialities associated with it."""
    matches = re.findall(r"\(([^)]+)\)", raw_subject_name)
    specialities_abbreviations = None

    if matches:
        specialities_abbreviations = matches[-1]

    def cleaned_string(s: str) -> str:
        """Return the string with only alphanumeric characters in lowercase."""
        return ''.join(filter(str.isalnum, s)).lower()

    if specialities_abbreviations:
        abbreviations = re.split(r'[+,]', specialities_abbreviations)
        specialities_for_subject = [
            sp for sp in all_specialities
            if any(cleaned_string(abb) in cleaned_string(sp) for abb in abbreviations)
        ]
        subject_name = raw_subject_name
        for match in matches:
            subject_name = subject_name.replace(f"({match})", "").strip()
    else:
        subject_name = raw_subject_name
        specialities_for_subject = all_specialities

    return subject_name, specialities_for_subject


def get_or_create_lesson(subject_name: str, all_subjects: Dict[str, Dict[str, Lesson]], speciality: str,
                         new_schedule_item: ScheduleItem) -> None:
    """Get or create a lesson based on the subject name and update its schedules."""
    existing_subjects = all_subjects[speciality]

    if subject_name in existing_subjects:
        lesson = existing_subjects[subject_name]
        matching_item = next((item for item in lesson if
                              item.type == new_schedule_item.type and
                              item.group == new_schedule_item.group and
                              item.time == new_schedule_item.time and
                              item.location == new_schedule_item.location and
                              item.day == new_schedule_item.day and
                              item.teachers == new_schedule_item.teachers), None)
        if matching_item:
            merged_item = merge_schedule_items(matching_item, new_schedule_item)
            lesson.remove(matching_item)
            lesson.append(merged_item)
        else:
            lesson.append(new_schedule_item)
    else:
        temp_lesson = [new_schedule_item]
        existing_subjects[subject_name] = temp_lesson


def sanitize_teacher_name(teacher: str) -> str:
    """Sanitize the teacher's name."""
    return teacher.replace('\n', '').strip()


def extract_teacher_and_subject(details: str) -> Tuple[str, List[str]]:
    """Extract teacher and subject from the given details, accounting for multiline strings."""
    teachers = []
    # Replace new lines with spaces and condense multiple spaces into one
    details = re.sub(r'\s+', ' ', details)

    title_pattern = '|'.join(TEACHER_TITLES)

    # Pattern to match initials before or after the surname
    teacher_pattern = re.compile(
        rf"({title_pattern})?\s*([А-ЯІЇЄ][.,]\s*[А-ЯІЇЄ][.,])?\s*([А-ЯІЇЄ][а-яіїє]+)\s*([А-ЯІЇЄ][.,]\s*[А-ЯІЇЄ][.,])?")
    matches = teacher_pattern.finditer(details)

    for match in matches:
        title, pre_initials, name, post_initials = match.groups()
        initials = pre_initials or post_initials
        if initials:
            full_name = (title + " " if title else "") + name + " " + initials.replace(",", ".").replace(" ", "")
            teachers.append(full_name.strip())
            details = details.replace(match.group().strip(), "").strip()

    details = details.rstrip(',').strip()

    return details, teachers


def extract_lesson_details(current_day, row, all_subjects: Dict[str, Dict[str, Lesson]],
                           all_specialities: List[str]) -> None:
    """Extract lesson details from a row and update the given lessons' dictionary."""
    time_slot = parse_time(row[1])
    raw_subject_details = row[2]
    subject_details = extract_teacher_and_subject(raw_subject_details)
    raw_subject_name = subject_details[0].strip()

    subject_name, specialities_for_subject = extract_subject_and_specialities(raw_subject_name, all_specialities)

    teachers = subject_details[1]
    pair_type, group = identify_pair_type_and_group(row[3])
    weeks = parse_weeks(row[4])
    location = row[5]

    new_schedule_item = ScheduleItem(
        type=pair_type,
        group=group,
        time=time_slot,
        weeks=weeks,
        location=location,
        day=current_day,
        teachers=teachers
    )

    for speciality in specialities_for_subject:
        get_or_create_lesson(subject_name, all_subjects, speciality, new_schedule_item)


def process_schedule(sheet, all_specialities: List[str]) -> Dict[str, Dict[str, list[Lesson]]]:
    """Process the entire schedule to extract lessons and group by subjects."""
    all_subjects = {speciality: {} for speciality in all_specialities}
    current_day = None

    for row in sheet.iter_rows(values_only=True):
        potential_day = identify_current_day(row[0])
        if potential_day:
            current_day = potential_day

        if current_day and row[1] and row[2]:
            extract_lesson_details(current_day, row, all_subjects, all_specialities)

    return all_subjects


def parse_schedules_from_workbook(workbook: Workbook) -> Dict[str, List[Schedule]]:
    """Parse a schedules from the given workbook."""
    sheet = workbook.active

    faculty, all_specialities, semester = get_headers_from_sheet(sheet)
    all_subjects = process_schedule(sheet, all_specialities)

    schedules_dict = {faculty: []}

    for speciality, subjects in all_subjects.items():
        schedules_dict[faculty].append(Schedule(speciality, semester, subjects))

    return schedules_dict
