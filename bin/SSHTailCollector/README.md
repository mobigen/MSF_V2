# SSHTailCollector

외부의 서버에 SSH 프로토콜 접속을 통하여 접속
실시간으로 Config에 지정된 외부서버의 디렉토리안을 감시하여 생성된 새로운 파일들을 읽어 Config에 지정된 로컬 디렉토리로 불러온다.
index에 적혀있는 파일과 그 이후에 생긴 최신의 파일만 확인하므로(정확히는 코드상에 그저 파일이름을 비교하는것만 되있음, mtime이나 atime 고려 X) 최신파일의 구별은 파일이름을 구성하는 날짜가 기준이 된다.


## How to use
```Bash
$ python  SSHTailCollector.py <SECTION> <ConfigFilePath>
```

## STDIN
없음

## STDOUT
```Bash
없음
```

## Configuration

**SSHTailCollector.conf**

|Section|Option|Range|Description|
|:-------:|:------------:|----------|-------------------------------------------|
|Log      | LOG          |(string)  | log가 저장될 경로                         |
|[Section]| HOST         |(string)  | 접속할 host IP                            |
|         | PORT         |(string)  | 접속할 host PORT                          |
|         | USER         |(string)  | 접속할 host ID                            |
|         | PASS         |(string)  | 접속할 host Password                      |
|         | RDIR         |(string)  | 감시할 외부 host의 디렉토리 경로          |
|         | PATN         |(string)  | 감시할 파일의 패턴                        |
|         | BASE         |(string)  | INDEX basename                            |
|         | LDIR         |(string)  | tail결과를 로컬에 저장할때의 디렉토리 경로|
|         | RIDX         |(string)  | index 저장할 디렉토리 경로                |
|         | INTV         |(string)  | (현재 코드내에서 사용하지 않음)           |
|         | UIDS         |(string)  | (현재 코드내에서 사용하지 않음)           |
|         | EPTN         |(string)  | (현재 코드내에서 사용하지 않음)           |


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
1. 우선 tmp, data, idx 디렉토리를 비워주세요
2. 본 예제는 해당 모듈을 실행시키고 SSH로 감시중인 디렉토리에 새로운 파일이 생겼을때 어떤 결과가 생기는지를 보여줍니다.
3. example을 실행시키면서 tmp 디렉토리에 어떤값이 채워지는지 확인하세요.
4. log를 확인해가면서 어떤 동작이 일어나는지 확인하세요.
