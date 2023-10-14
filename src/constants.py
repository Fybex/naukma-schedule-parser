SCHEDULES_URLS = [
    'https://my.ukma.edu.ua/files/schedule/2023/1/1472/3.xlsx',
    'https://my.ukma.edu.ua/files/schedule/2023/1/1470/3.doc',
]

TEACHER_TITLES = sorted([
    "викл\.+",
    "(?:с|c)т\. ?викл\.+",
    "проф\.+",
    "доц\.+",
    "асист\.+",
    "ас\.+",
], key=len, reverse=True)

DOWNLOADED_SCHEDULES_DIR = '../data/downloaded_schedules/'
PARSED_SCHEDULES_DIR = '../data/parsed_schedules'
