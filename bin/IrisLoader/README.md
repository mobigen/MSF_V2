# IrisLoader.py

1. STDIN으로 DAT파일 경로가 입력 (ex: file://KEY_PARTITION.dat)
2. DAT파일을 읽어서 config로 읽은 CTL 파일을 이용해 IRIS에 로드
3. Config의 STDOUT 옵션이 STDOUT으로 처리된 DAT 파일의 경로를 출력
4. IRIS에 로드 실패시 Config에 지정된 디렉토리에 해당 dat 파일 보관

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
|         | FILE_REMOVE  |'Y', 'N'  | Load 완료된 dat파일 지울지 여부           |
|         | KEY_FILTER   |(string)  | KEY Filter, 해당하는 Key는 걸러짐         |
|         | TIMEOUT      |(string)  | IRIS Connector timeout 설정               |
|         | SEPARATE     |(string)  | 구분자 설정                               |
|         | STDOUT       |'Y', 'N'  | Load완료 후 STDOUT으로 해당 파일 출력 여부|
|         | ERROR_PATH   |(string)  | Load 에러시 해당 dat파일을 보관할 디렉토리|
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
$ pylint --disable=C --disable=E0602 --msg-template='{path}:{line}:[{msg_id}({symbol}),{obj}]{msg}' *.py
```

## Example
  1. 우선 테스트할 아이리스서버에 TEST_TABLE 테이블이 있다면 삭제하세요.
  2. example.sh를 실행시키면 TEST_TABLE 테이블을 생성하고 해당 모듈을 실행시켜 stdin으로 file://data/k_20110616000000.dat 을 입력하게 됩니다.
  3. 해당 아이리스 서버에서 TEST_TABLE 테이블에 데이터가 들어갔는지 확인하세요.
