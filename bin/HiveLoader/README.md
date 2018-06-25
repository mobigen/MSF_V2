# HIVELoader

**CSV(file path specified in STDIN) -> HIVE(table name, partition specified in STDIN)**

STDIN으로 들어온 table을 Oracle의 특정 테이블을 참조한다.
Oracle의 특정 테이블의 컬럼은 Table이름, 해당 Hive의 Table을 생성하기 위한 장문의 Hive DDL 로 이루어져 있다. 이 테이블을 참조하여 Hive에 특정 테이블을 생성할 수 있는 DDL을 얻을 수 있으며 이 모듈은 해당 DDL를 사용하여 Hive에 Table을 만들게 된다.
그리고 STDIN으로 들어온 Path의 CSV파일을 해당 Hive의 Table로 로드하게 된다.

**STDIN form**
```Bash
<table>://<path>||<partition>
```

## How to use
```Bash
$ python <ConfigFilePath>
```

## Configuration

**HiveLoader.conf**

|Section |Option         |Range      |Description                                    |
|:------:|:-------------:|-----------|-----------------------------------------------|
|Log     | LogFilePath   | (string)  | log가 저장될 경로                             |
|        | LogFileSize   | (int)     | log파일의 최대 사이즈                         |
|        | LogFileCount  | (int)     | log파일의 최대 수                             |
|DB      | DB_TYPE       | (string)  | 접속할 ftp host 주소                          |
|        | DB_CONFPATH   | (string)  | 접속할 ftp port                               |
|        | DB_SECTION    | (string)  | 접속할 ftp id                                 |
|HIVE    | IP            | (string)  | 접속할 Hive host IP                           |
|        | PORT          | (int)     | 접속할 Hive port                              |
|        | USERNAME      | (string)  | 접속할 HDFS user name                         |
|        | DATABASE      | (string)  | 접속할 Hive Database                          |

## Prerequisites
- Python == 2.7
- python-devel
- cyrus-sasl
- cyrus-sasl-devel

## How to unit test (Dynamic test)
```Bash
$ nosetests -v --with-coverage --with-doctest --cover-erase --exe  --cover-package=. tests/*.py
```

## How to lint test (Static test)
```Bash
$ pylint --disable=C --disable=E0602 --msg-template='{path}:{line}:[{msg_id}({symbol}),{obj}]{msg}' *.py
```

## Example
1. 해당 HDFS에 접속을 하여 config와 example의 예제로 들어가는 stdin의 파티션에 해당하는 디렉토리를 비워주세요.
2. example을 실행시키면 stdin으로 들어온 partition을 통해 HDFS에 디렉토리를 생성하고 그 디렉토리에 해당 파일을 저장하게 됩니다.
3. example 실행이 끝난 뒤 해당 HDFS 디렉토리에 어떤 파일이 생성되었는지 확인하세요.
