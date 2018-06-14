# IrisLoader.py

1. STDIN으로 DAT파일 경로가 입력 (ex: file://KEY_PARTITION.dat)
2. DAT파일을 읽어서 config로 읽은 CTL 파일을 이용해 IRIS에 로드
3. STDOUT으로 처리된 DAT 파일의 경로를 출력

## How to use
```Bash
$ python IrisLoader.py <Section> <ConfigFilePath>
```

## Configuration

**Aggregator.conf**

|Section|Option|Range|Description|
|:-------:|:------------:|----------|-------------------------------------------|
|Log      | logfilepath  |(string)  | log가 저장될 경로                         |
|         | logfilesize  |(int)     | log파일의 최대 사이즈                     |
|         | logfilecount |(int)     | log파일의 최대 수                         |
|IRIS     | IRIS_IP      |(string)  | 접속할 IRIS host IP                       |
|         | IRIS_ID      |(string)  | 접속할 IRIS host ID                       |
|         | IRIS_PWD     |(string)  | 접속할 IRIS host ID의 패스워드            |
|         | CTL_PATH     |(string)  | CTL파일 경로                              |
|         | TABLE        |(string)  | Load할 테이블                             |
|         | FILE_REMOVE  |(string)  | Load 완료된 dat파일 지울지 여부           |
|         | KEY_FILTER   |(string)  | KEY Filter, 해당하는 Key는 걸러짐         |
|         | TIMEOUT      |(string)  | IRIS Connector timeout 설정               |
|         | SEPARATE     |(string)  | 구분자 설정                               |
|         | STDOUT       |(string)  | Load완료 후 STDOUT으로 해당 파일 출력 여부|
|[Section]| TABLE        |(string)  | Load할 테이블                             |
|         | KEY_FILTER   |(string)  | KEY Filter, 해당하는 Key는 걸러짐         |
|         | FILE_REMOVE  |(string)  | Load 완료된 dat파일 지울지 여부           |
|         | STDOUT       |(string)  | Load완료 후 STDOUT으로 해당 파일 출력 여부|

## Prerequisites
- Python == 2.7

## How to unit test (Dynamic test)
```Bash
$ nosetests -v --with-coverage --with-doctest --cover-erase --exe  --cover-package=. tests/*.py
```

## How to lint (Static test)
```Bash
$ pylint --disable=C --disable=E0602 --extension-pkg-whitelist=MySQLdb,cx_Oracle --generated-members=message,code,ProgrammingError,OperationalError --msg-template='{path}:{line}:[{msg_id}({symbol}),{obj}]{msg}' *.py
```
