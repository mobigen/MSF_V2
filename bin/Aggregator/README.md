# Aggregator

**CSV -> Aggregation -> STORAGE**

STDIN으로 들어온 Path의 CSV파일을 집계(SUM, COUNT, ...)하여 STORAGE(MySQL, Oracle, File ...)로 로드
현재 STDIN의 prefix는 역할이 없으므로 필요에 맞게 수정하여 사용 가능

## How to use
```Bash
$ python Aggregator.py <Section> <ConfigFilePath>
```

## STDIN
```Bash
file://<File path>
```

## STDOUT
없음

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
|| STORAGE_TYPE   |(string)| Load할 STORAGE Type(ex: MySQL, Oracle, File...)    |
|| STORAGE_CONFPATH   |(string)| Load할 STORAGE의 config가 저장된 경로   |
|| STORAGE_SECTION   |(string)| Load할 STORAGE의 config의 section        |
|| STORAGE_TABLE   |(string)| Load할 STORAGE의 테이블(STORAGE에 테이블 없을시 자동으로 생성됨) |

**MySQL.conf**

MySQL 접속정보를 기재해놓습니다.

|Section  |Option  |Range   |Description         |
|:-------:|:------:|--------|--------------------|
|[Section]|HOST    |(string)|접속할 Host주소     |
|         |PORT    |(int)   |접속할 Port         |
|         |ID      |(int)   |접속할 ID           |
|         |PWD     |(int)   |접속할 PWD          |
|         |DB      |(int)   |접속할 DB           |

**Oracle.conf**

Oracle 접속정보를 기재해놓습니다.

|Section  |Option  |Range   |Description         |
|:-------:|:------:|--------|--------------------|
|[Section]|HOST    |(string)|접속할 Host주소     |
|         |PORT    |(int)   |접속할 Port         |
|         |ID      |(string)|접속할 ID           |
|         |PWD     |(string |접속할 PWD          |
|         |SID     |(string)|접속할 SID          |


**File.conf**

저장할 File을 기재해놓습니다.

|Section  |Option  |Range         |Description                     |
|:-------:|:------:|--------------|--------------------------------|
|[Section]|DIRPATH |(string)      |저장할 파일의 디렉토리경로      |
|         |FILENAME|(string)      |저장할 파일의 이름              |
|         |SEP     |(string)      |구분자 설정                     |
|         |MODE    |a, w          |python file mode append or write|
|         |INDEX   |True, False   |row index 출력 유무             |

http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_csv.html#pandas.DataFrame.to_csv 를 참고하여 해당 옵션을 더 추가할 수 있습니다.

**Aggregator.conf.enc**

암호화된 Aggregator.conf 파일입니다.

**KEY**

암호화한 파일을 볼 수 있게 해주는 KEY 파일입니다.


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

## Example
1. 우선 Config에 설정된 DB 접속여부를 확인하시고 Config에 입력된 Table과 중복되는 Table이 있는지 확인하세요.
1. 해당 모듈을 실행시키고 STDIN으로 file://data/test_file.csv 을 입력했을 때 어떤 결과가 나오는지 확인 할 수 있습니다.
2. Config로 설정한 결과가 해당 DB에서 제대로 생성됬는지 확인하시고 로그를 확인하세요.
