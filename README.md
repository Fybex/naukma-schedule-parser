# naukma-schedule-parser

`naukma-schedule-parser` is a Python tool for parsing and processing schedules from the National University of
Kyiv-Mohyla
Academy (NaUKMA) website. It can extract schedule data from Excel and Word documents and save it in a structured format.

## Getting Started

Follow these steps to set up and use naukma-schedule-parser.

### Installation

1. Clone the `naukma-schedule-parser` repository:

```shell
git clone https://github.com/Fybex/naukma-schedule-parser.git
```

2. Change to the project directory:

```shell
cd naukma-schedule-parser
```

3. Install the required dependencies:

```shell
pip install -r requirements.txt
```

### Configuration

1. Open the `src/config.py` file in a text editor.
2. Configure the following settings as needed:
    - `USE_SCHEDULES_FROM_URLS`: Set to True if you want to use schedules from URLs, or False to use local files.
    - `SCHEDULES_URLS`: List of URLs to schedule documents.
    - `DOWNLOADED_SCHEDULES_DIR`: Directory where downloaded from URLs schedules will be saved
      if `USE_SCHEDULES_FROM_URLS` is set to True. Otherwise, directory where local schedules to parse are located.
    - `PARSED_SCHEDULE_DIR`: Directory where parsed `schedule.json` will be saved.

### Usage

1. Run the `src/main.py` script:

```shell
python src/main.py
```

2. The parsed schedule will be saved in the `PARSED_SCHEDULE_DIR` directory in the `schedule.json` file.


