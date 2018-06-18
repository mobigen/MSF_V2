# Kafka Modules
1. Producer가 STDIN을 입력 받음 (STDIN format : DATE://[YYYYmmddHHMMSS])
2. Producer가 STDIN으로 들어온 DATE와 Config에 입력된 쿼리를 바탕으로 해당하는 DB에 쿼리를 입력하여 결과를 얻는다.
3. Config에 입력된 크기의 수로 데이터를 나눈 후 나눈 데이터마다 Config에 설정된 Start delimiter와 End delimiter 를 기준으로 나눠 데이터를 Broker server로 전송한다.
4. MessageMonitor가 해당 메세지들을 입력받는다. End delimiter가 메세지로 전송될 경우 현재까지 쌓인 큐의 데이터를 Config에 입력된 경로로 csv파일로 덤프하게 된다.

## How to use
**Producer**
```Bash
$ python Producer.py <Section> <ConfigFilePath>
```
이 때 Section은 카프카서버의 토픽 이름이 된다.

**MessageMonitor**
```Bash
$ python MessageMonitor.py <Section> <ConfigFilePath>
```
이 때 Section은 카프카서버의 토픽 이름이 된다.

## Configuration

**Producer.conf**

|Section|Option|Range|Description|
|:------:|:-------------:|-----------|-----------------------------|
|Log     |logfilepath    | (string) |  log가 저장될 경로           |
|        |logfilesize    | (int)      |   log파일의 최대 사이즈   |
|        |logfilecount   | (int)      |   log파일의 최대 수          |
|Kafka   |  |  | https://kafka.apache.org/documentation/#producerconfigs 참고|
|Section | DB_TYPE       |MySQL, Oracle| 해당 Topic의 데이터를 생성할 DB를 선택함|
|        | DB_CONFPATH   |(string)| 해당 DB의 Config 경로|
|        | DB_SECTION    |(string)| 해당 DB의 Config Section|
|        | QUERY         |(string)| STDIN으로 받은 데이터와 조합하여 실행할 query|
|        | VOLUME        |(string)| 파일로 dump할 때 파일 하나의 최대 Row 개수 |
|        | COL_DELIMITER |(string)| DB로 받은 데이터를 broker로 보낼때의 컬럼구분자|

**MessageMonitor.conf**

|Section|Option|Range|Description|
|:------:|:-------------:|-----------|-----------------------------|
|Log     |logfilepath    | (string) |  log가 저장될 경로           |
|        |logfilesize    | (int)      |   log파일의 최대 사이즈   |
|        |logfilecount   | (int)      |   log파일의 최대 수          |
|Section |START_DELIMITER|(string)|메시지의 시작을 알리는 구분자  |
|        |END_DELIMITER  |(string)|메시지의 끝을 알리는 구분자. 지금까지 받은 메시지를 파일로 덤프시킨다. |
|        |INDEX_FILE     |(string)|모듈이 중간에 종료됬을때 인덱스 파일을 저장하기 위함 (기능안함)|
|        |DUMP_PATH      |(string)|파일이 덤프될 위치의 경로|
|        | 그외   || https://kafka.apache.org/documentation/#consumerconfigs 참고|

**MySQL.conf**

|Section  |Option|Range   |Description|
|:-------:|:----:|:------:|--------------------|
|[SECTION]|HOST  |(string)| MySQL Host IP      |
|         |PORT  |(int)   | MySQL Host Port    |
|         |ID    |(string)| MySQL 접속 ID      |
|         |PWD   |(string)| MySQL 접속 Password|
|         |DB    |(string)| MySQL 접속 DB      |

**Oracle.conf**

|Section  |Option|Range   |Description|
|:-------:|:----:|:------:|--------------------|
|[SECTION]|HOST  |(string)| Oracle Host IP      |
|         |PORT  |(int)   | Oracle Host Port    |
|         |ID    |(string)| Oracle 접속 ID      |
|         |PWD   |(string)| Oracle 접속 Password|
|         |SID    |(string)| Oracle 접속 SID    |

## Prerequisites
- Python == 2.7
- cx_Oracle >= 6.3.1
- librdkafka >= 0.9.5
	- The GNU toolchain
	- GNU make
	- pthreads
	- zlib (optional, for gzip compression support)
	- libssl-dev (optional, for SSL and SASL SCRAM support)
	- libsasl2-dev (optional, for SASL GSSAPI support)

## How to unit test (Dynamic test)
```Bash
$ nosetests -v --with-coverage --with-doctest --cover-erase --exe  --cover-package=. tests/*.py
```

## How to lint (Static test)
```Bash
$ pylint --disable=C --disable=E0602 --extension-pkg-whitelist=MySQLdb,cx_Oracle --generated-members=message,code,ProgrammingError,OperationalError --msg-template='{path}:{line}:[{msg_id}({symbol}),{obj}]{msg}' *.py
```
