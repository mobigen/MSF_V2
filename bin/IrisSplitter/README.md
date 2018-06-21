# IrisSplitter
Stdin 으로 받은 file을 IRIS에 Loading하기 위해 Key와 Partition별로 분할저장합니다.
서버의 시스템 시각 기준으로 저장하는 형식과, 로그파일의 사용자 시각 기준으로 저장하는 형식 두가지를 제공합니다.

## How to use
```Bash
$ python <Section> <ConfigPath>
```

## STDIN
```Bash
<STDIN_STRING><FilePath>
```
예를 들어 Config파일의 STDIN_STRING이 file:// 로 설정 되어 있고 현재 디렉토리의 test.csv를 받는다면
```Bash
file://test.csv
```

## STDOUT
```Bash
file://<저장된 FilePath>
```

## Configuration

**IrisSplitter.conf**

|Section  |Option          |Range   |Description|
|:-------:|:--------------:|--------|------------------------------------------------|
|Log      |logfilepath     |(string)| log가 저장될 경로                              |
|         |logfilesize     |(int)   | log파일의 최대 사이즈                          |
|         |logfilecount    |(int)   | log파일의 최대 수                              |
|COMMON   |SAVE_PATH       |(string)| 결과를 저장할 디렉토리 경로                    |
|         |FILE_SEPARATE   |(string)| 읽는 파일의 열 구분자                          |
|         |SAVE_SEPARATE   |(string)| 저장할 파일의 열 구분자                        |
|         |STDIN_STRING    |(string)| STDIN의 Header 지정                            |
|         |KEY_INDEX       |(int)   | Key 인덱스                                     |
|         |KEY_START_INDEX |(int)   | Key 인덱스 슬라이스시 시작점                   |
|         |KEY_END_INDEX   |(int)   | Key 인덱스 슬라이스시 끝점                     |
|         |PARTITION_RANGE |(int)   | 여러개의 파일로 나눌 기준이 될 Partition Range |
|         |PRATITION_INDEX |(int)   | Partition_Range를 적용할 Partition Index       |
|<Section>|                || COMMON 섹션과 동일, 추가 적용할 옵션 덮어씌우기 용     |

## Prerequisites
- Python == 2.7
- Python-M6-API == 1.1

## How to unit test (Dynamic test)
```Bash
$ nosetests -v --with-coverage --with-doctest --cover-erase --exe  --cover-package=. tests/*.py
```

## How to lint (Static test)
```Bash
$ pylint --disable=C --disable=E0602 --msg-template='{path}:{line}:[{msg_id}({symbol}),{obj}]{msg}' *.py
```

## Example
1. 우선 tmp 디렉토리를 비워주세요.
2. 해당 모듈을 실행시키고 STDIN으로 file://data/MSF_TEST-0-20180616000000.dat 을 주었을때 tmp 디렉토리에 어떤 결과들이 생성되는지 확인하세요.
3. 로그를 확인하세요.
