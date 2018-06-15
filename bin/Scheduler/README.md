# Scheduler
crontab 방식으로 정기적으로 시간을 STDOUT으로 출력하는 모듈

## How to use
```Bash
$ python Scheduler.py <Section> <ConfigFilePath>
```

## Configuration

**Scheduler.conf**

|Section  |Option       |Range    |Description|
|:-------:|:-----------:|---------|-----------------------------|
|GENERAL  |LOG_DIR      |(string) | 로그가 저장될 디렉토리 경로 |
|[Section]| YEAR        |(int|str)| 4-digit year number        |
|         | MONTH       |(int|str)| month number (1-12)      |
|         | DAY         |(int|str)| day of the month (1-31)   |
|         | WEEK        |(int|str)| ISO week number (1-53)       |
|         | DAY_OF_WEEK |(int|str)| number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)     |
|         | HOUR        |(int|str)| hour (0-23)    |
|         | MINUTE      |(int|str)| (0-59)  |
|         | SECOND      |(int|str)| (0-59)     |
|         | OUTPUT      |(int|str)| 출력할 OUTPUT 형식   |

## STDIN
없음

## STDOUT
Config를 통해 설정될 수 있음

## Prerequisites
- Python ==2.7

## How to unit test (Dynamic test)
```Bash
$ nosetests -v --with-coverage --with-doctest --cover-erase --exe  --cover-package=. tests/*.py
```

## How to lint (Static test)
```Bash
$ pylint --disable=C --disable=E0602 --extension-pkg-whitelist=MySQLdb,cx_Oracle --generated-members=message,code,ProgrammingError,OperationalError --msg-template='{path}:{line}:[{msg_id}({symbol}),{obj}]{msg}' *.py
```

