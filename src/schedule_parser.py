import re
from openpyxl import Workbook
from typing import List, Dict, Tuple

from utils import (
    detect_day,
    fetch_specialities,
    determine_lesson_type_and_group,
    convert_to_time,
    extract_weeks,
    keyword_exists,
    simplify_string,
)
from schedule_types import Schedule, ScheduleItem, Lesson
from constants import (
    TEACHER_TITLES,
    FACULTY_KEYWORD,
    SPECIALITY_KEYWORD,
    SEMESTER_KEYWORD,
)

__all__ = ["parse_workbook_to_schedules"]


def get_sheet_headers(sheet) -> Tuple[str | None, List[str], str | None]:
    """Retrieve faculty, specialties, and semester information from an Excel sheet."""
    faculty, specialty, semester = None, None, None

    for row in sheet.iter_rows(values_only=True):
        for cell in row:
            if cell:
                if detect_day(cell):
                    return faculty, fetch_specialities(specialty), semester

                cell_content = cell.lower()

                if keyword_exists(cell_content, FACULTY_KEYWORD):
                    faculty = cell
                elif keyword_exists(cell_content, SPECIALITY_KEYWORD):
                    specialty = cell
                elif keyword_exists(cell_content, SEMESTER_KEYWORD):
                    semester = cell

    return faculty, fetch_specialities(specialty), semester


def combine_schedule_items(item1: ScheduleItem, item2: ScheduleItem) -> ScheduleItem:
    """Combine two schedule items."""
    merged_weeks = sorted(list(set(item1.weeks + item2.weeks)))
    return ScheduleItem(
        type=item1.type,
        group=item1.group,
        time=item1.time,
        weeks=merged_weeks,
        location=item1.location,
        day=item1.day,
        teachers=item1.teachers,
    )


def extract_subject_and_associated_specialities(
    raw_name: str, all_specialities: List[str]
) -> Tuple[str, List[str]]:
    """Separate the subject name from its associated specialties."""
    matches = re.findall(r"\(([^)]+)\)", raw_name)
    specialities_codes = matches[-1] if matches else None

    if specialities_codes:
        codes = re.split(r'[+,]', specialities_codes)
        subject_specialities = [
            sp
            for sp in all_specialities
            if any(simplify_string(code) in simplify_string(sp) for code in codes)
        ]
        subject = raw_name.replace(f"({specialities_codes})", "").strip()
    else:
        subject = raw_name
        subject_specialities = all_specialities

    return subject, subject_specialities


def add_or_update_lesson(
    subject: str,
    all_lessons: Dict[str, Dict[str, Lesson]],
    specialty: str,
    schedule_item: ScheduleItem,
) -> None:
    """Insert a new lesson or update an existing one."""
    current_lessons = all_lessons.get(specialty, {})
    lesson = current_lessons.get(subject, [])

    matching_item = next(
        (
            item
            for item in lesson
            if item.type == schedule_item.type
            and item.group == schedule_item.group
            and item.time == schedule_item.time
            and item.location == schedule_item.location
            and item.day == schedule_item.day
            and item.teachers == schedule_item.teachers
        ),
        None,
    )

    if matching_item:
        updated_item = combine_schedule_items(matching_item, schedule_item)
        lesson.remove(matching_item)
        lesson.append(updated_item)
    else:
        lesson.append(schedule_item)

    current_lessons[subject] = lesson
    all_lessons[specialty] = current_lessons


def clean_teacher_name(name: str) -> str:
    """Remove unnecessary characters from the teacher's name."""
    return name.replace('\n', '').strip()


def extract_teacher_and_subject_info(detail: str) -> Tuple[str, List[str]]:
    """Get teacher and subject information from the provided string."""
    teacher_list = []
    detail = re.sub(r'\s+', ' ', detail)
    title_pattern = '|'.join(TEACHER_TITLES)
    teacher_regex = re.compile(
        rf"({title_pattern})?\s*([А-ЯІЇЄ][.,]\s*[А-ЯІЇЄ][.,])?\s*([А-ЯІЇЄ][а-яіїє]+)\s*([А-ЯІЇЄ][.,]\s*[А-ЯІЇЄ][.,])?"
    )
    matches = teacher_regex.finditer(detail)

    for match in matches:
        title, pre_initials, name, post_initials = match.groups()
        initials = pre_initials or post_initials
        if initials:
            full_name = (
                (title + " " if title else "")
                + name
                + " "
                + initials.replace(",", ".").replace(" ", "")
            )
            teacher_list.append(full_name.strip())
            detail = detail.replace(match.group().strip(), "").strip()

    detail = detail.rstrip(',').strip()

    return detail, teacher_list


def extract_lesson_info_from_row(
    day, row, all_lessons: Dict[str, Dict[str, Lesson]], all_specialities: List[str]
) -> None:
    """Get lesson details from a given row."""
    time_interval = convert_to_time(row[1])
    details, teachers = extract_teacher_and_subject_info(row[2])
    subject, subject_specialities = extract_subject_and_associated_specialities(
        details, all_specialities
    )
    lesson_type, group = determine_lesson_type_and_group(row[3])
    weeks = extract_weeks(row[4])
    location = row[5]

    schedule_item = ScheduleItem(
        type=lesson_type,
        group=group,
        time=time_interval,
        weeks=weeks,
        location=location,
        day=day,
        teachers=teachers,
    )

    for speciality in subject_specialities:
        add_or_update_lesson(subject, all_lessons, speciality, schedule_item)


def extract_lessons_from_sheet(
    sheet, all_specialities: List[str]
) -> Dict[str, Dict[str, List[Lesson]]]:
    """Retrieve lessons from the sheet and categorize them by subject."""
    lessons_by_subject = {speciality: {} for speciality in all_specialities}
    current_day = None

    for row in sheet.iter_rows(values_only=True):
        day_in_row = detect_day(row[0])
        if day_in_row:
            current_day = day_in_row

        if current_day and row[1] and row[2]:
            extract_lesson_info_from_row(
                current_day, row, lessons_by_subject, all_specialities
            )

    return lessons_by_subject


def parse_workbook_to_schedules(workbook: Workbook) -> Dict[str, List[Schedule]]:
    """Parse the provided workbook to extract schedules."""
    sheet = workbook.active

    faculty, specialities, semester = get_sheet_headers(sheet)
    lessons_by_subject = extract_lessons_from_sheet(sheet, specialities)

    schedules = {
        faculty: [
            Schedule(speciality, semester, subjects)
            for speciality, subjects in lessons_by_subject.items()
        ]
    }

    return schedules
