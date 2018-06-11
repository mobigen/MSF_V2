# Aggregator

**CSV -> Aggregation -> DB**

STDIN으로 들어온 Path의 CSV파일을 집계(SUM, COUNT, ...)하여 DB(MySQL, Oracle, ...)로 로드
현재 STDIN의 prefix는 역할이 없으므로 필요에 맞게 수정하여 사용 가능

## How to use
```Bash
$ python Aggregator.py <Section> <ConfigFilePath>
```

## Configuration

**Aggregator.conf**

|Section|Option|Range|Description|
|:------:|:-------------:|-----------|-----------------------------|
|Log    |logfilepath    | (string) |  log가 저장될 경로           |
|          |logfilesize     | (int)      |   log파일의 최대 사이즈   |
|          |logfilecount  | (int)      |   log파일의 최대 수          |
|Section| SEP   |(string)| 읽을 csv파일의 컬럼 구분자        |
|| GROUPBY   |(string)| groupby 할 컬럼 이름들      |
|| SUM   |(string)| SUM 연산할 컬럼   |
|| MAX   |(string)| MAX 연산할 컬럼       |
|| MIN   |(string)| MIN 연산할 컬럼      |
|| COUNT   |(string)| COUNT 연산할 컬럼     |
|| DB_TYPE   |(string)| Load할 DB Type(ex: MySQL, Oracle, ...)    |
|| DB_CONFPATH   |(string)| Load할 DB의 config가 저장된 경로   |
|| DB_SECTION   |(string)| Load할 DB의 config의 section        |
|| DB_TABLE   |(string)| Load할 DB의 테이블   |

## Prerequisites
- Python == 2.7
- cx_Oracle >= 6.3.1

## How to unit test (Dynamic test)
```Bash
$ nosetests -v --with-coverage --with-doctest --cover-erase --exe  --cover-package=. tests/*.py
```

## How to lint (Static test)
```Bash
$ pylint --disable=C --disable=E0602 --extension-pkg-whitelist=MySQLdb,cx_Oracle --generated-members=message,code,ProgrammingError,OperationalError --msg-template='{path}:{line}:[{msg_id}({symbol}),{obj}]{msg}' *.py
```
