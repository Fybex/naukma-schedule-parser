from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class DayOfWeek(Enum):
    MONDAY = "Понеділок"
    TUESDAY = "Вівторок"
    WEDNESDAY = "Середа"
    THURSDAY = "Четвер"
    FRIDAY = "П'ятниця"
    SATURDAY = "Субота"


class PairType(Enum):
    LECTURE = "лекція"
    PRACTICE = "практика"
    UNKNOWN = "невизначено"


@dataclass
class TimeSlot:
    start: str
    end: str


@dataclass
class ScheduleItem:
    type: PairType
    group: Optional[str]
    time: TimeSlot
    weeks: List[int]
    location: str
    day: DayOfWeek
    teachers: Optional[List[str]]


Lesson = List[ScheduleItem]


@dataclass
class Schedule:
    speciality: str
    semester: Optional[str]
    subjects: Dict[str, List[Lesson]]
