# MySQLHandler

MySQL을 핸들링 하기 위한 모듈

## How to use
MySQLHandler를 쓰고 싶은 모듈에서 import해서 사용

## initiate
```Python
db_obj = MySQLHandler(<section>, <ConfigParser.ConfigParser instance>)
```
section : MySQL config 해당 섹션

## API
|Method|Args|Description|
|:----:|:--:|:---------:|
|MySQLHandler.connect||연결|
|MySQLHandler.disconnect||연결해제|
|MySQLHandler.executeGetData|sql, retry=0|쿼리문 실행 후 결과 리턴, 실패시 False 리턴|
|MySQLHandler.executeQuery|sql, retry=0|쿼리문 실행, 실패 시 False 리턴|

##Configuration

**MySQL.conf**

|Section  |Option|Range   |Description|
|:-------:|:----:|:------:|--------------------|
|[SECTION]|HOST  |(string)| MySQL Host IP      |
|         |PORT  |(int)   | MySQL Host Port    |
|         |ID    |(string)| MySQL 접속 ID      |
|         |PWD   |(string)| MySQL 접속 Password|
|         |DB    |(string)| MySQL 접속 DB      |

## Prerequisites
- Python == 2.7
- mysql-client, mysql-libs >= 5.1

## How to unit test (Dynamic test)
```Bash
$ nosetests -v --with-coverage --with-doctest --cover-erase --exe  --cover-package=. tests/*.py
```

## How to lint (Static test)
```Bash
$ pylint --disable=C --disable=E0602 --extension-pkg-whitelist=MySQLdb --generated-members=ProgrammingError,OperationalError --msg-template='{path}:{line}:[{msg_id}({symbol}),{obj}]{msg}' *.py
```
