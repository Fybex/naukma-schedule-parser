TEACHER_TITLES = sorted([
    "викл\.+",
    "(?:с|c)т\. ?викл\.+",
    "проф\.+",
    "доц\.+",
    "асист\.+",
    "ас\.+",
], key=len, reverse=True)

FACULTY_KEYWORD = "факультет"
SPECIALITY_KEYWORD = "спеціальність"
SEMESTER_KEYWORD = "семестр"
