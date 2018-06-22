# LoadManager.py

1. STDIN으로 config파일 경로가 입력 (ex: file://conf/TEST_2.conf)
2. Config에 있는 소스 DB에서 쿼리문 날린 결과를 목적 DB로 삽입

## How to use
```Bash
$ python LoadManager.py <LogFileName> <ConfigFilePath>
```

## Configuration

**LoadManager.conf**

|Section|Option|Range|Descrption|
|:-------:|:------------:|----------|-------------------------------------------|
|Log      | log_dir  |(string)  | log가 저장될 경로                         |
|         | log_line  |(int)     | log파일의 최대 사이즈                     |
|         | log_divide |(int)     | log파일의 최대 수                         |

**[STDIN으로 들어갈 config]**

|Section|Option|Range|Description|
|:-------:|:------------------:|----------|-------------------------------------------|
|GENERAL  | SRC_DBMS           |(string)  | Source DBMS(IRIS, ORACLE, MYSQL 값 중 하나|
|         | SRC_IP             |(string)  | Source DBMS의 IP 주소                     |
|         | SRC_PORT           |(string)  | Source DBMS 포트                          |
|         | SRC_DB             |(string)  | Source DBMS의 DB명(오라클은 SID)          |
|         | SRC_ID             |(string)  | Source DBMS의 user id                     |
|         | SRC_PWD            |(string)  | Source DBMS의 user password           |
|         | SRC_ENC            |(string)  | Source DBMS의 Encoding Type(utf-8의 경우, "utf8"로 작성해야 함         |
|         | DST_DBMS           |(string)  | Destination DBMS(IRIS, ORACLE, MYSQL값 중 하나   |
|         | DST_IP             |(string)  | Destination DBMS의 IP 주소    |
|         | DST_PORT           |(string)  | Destination DBMS의 Port  |
|         | DST_DB             |(string)  | Destination DBMS의 DB명(오라클은 SID) |
|         | DST_ID             |(string)  | Destination DBMS의 user id  |
|         | DST_PWD            |(string)  | Destination DBMS의 user password  |
|         | DST_TABLE          |(string)  | Destination DBMS에 loading해야하는 테이블  |
|         | DST_ENC            |(string)  | Destination DBMS의 Encoding Type  |
|         | DATA_DIR           |(string)  | Load관련 데이터 파일을 저장할 디렉토리  |
|         | COLSEP             |(string)  | column separator  |
|         | ROWSEP             |(string)  | row separator  |
|         | SQL                |(string)  | Source DBMS에서 데이터를 가져올 쿼리  |
|IRIS     | KEY_INDEX          |(int)     | Key컬럼의 위치(1부터 시작)                |
|         | KEY_PARSE          |(int)     | 1인 경우 keyindex 사용, 2인 경우 key count로 분리, 3인 경우 특정 위치 KEY_LEN자리로 생성 |
|         | KEY_LEN            |(int)     | KEY_PARSE가 3인 경우 처리할 key컬럼의 뒷자리 갯수          |
|         | KEY_COUNT          |(int)     | KEY_PARSE가 2인 경우 key 생성 개수        |
|         | DATE_TIME_INDEX    |(int)     | Partition 컬럼 위치(1부터 시작)           |
|         | PARTITION_TERM     |'Y', 'N'  | Partition 주기                            |
|         | COLUMN             |(string)  | LOAD할 테이블의 컬럼 정보                 |
|         | LOAD_THREAD_COUNT  |(string)  | LOAD시 생성할 Thread 수                   |
|DBMS     | ORACLE_LOADER      |(string)  | Oracle Loader                             |
|         | MYSQL_LOADER       |(string)  | MYSQL_Loader                              |
|         | CONTROL_FILE_ORACLE|(string)  | Oracle loading시 사용하는 control file    |
|         | LOG_FILE           |(string)  | loader에서 필요로 하는 로그파일           |

## Prerequisites
- Python == 2.7
- cx_Oracle >= 6.3.1

## How to unit test (Dynamic test)
```Bash
$ nosetests -v --with-coverage --with-doctest --cover-erase --exe  --cover-package=. tests/*.py
```

## How to lint (Static test)
```Bash
$ pylint --disable=C --disable=E0602 --msg-template='{path}:{line}:[{msg_id}({symbol}),{obj}]{msg}' *.py
```

## Example
  1. 우선 테스트할 아이리스 서버와 오라클 서버에 TEST_TABLE 테이블이 있다면 삭제하세요.
  2. example.sh를 실행시키면 아이리스와 오라클에 TEST_TABLE 테이블을 생성하고 오라클에 테스트 데이터를 삽입하게 됩니다.
  3. 그 후 본문의 모듈이 시작되게 되고 STDIN으로 file://conf/TEST.conf 을 받게 됩니다.
  4. STDIN으로 입력받은 config 경로를 찾아 읽게 되고 설정되있는 Config에 따라 오라클에서 아이리스로 데이터를 로드하게 됩니다.
  5. tmp 디렉토리와 log 디렉토리에 어떤것이 생겼는지 확인하세요.


