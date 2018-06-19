# FilePatternMonitor

**Monitoring files in directory -> STDOUT**

Config에 지정된 DIRECTORY안에 FILE_PATTERN과 일치하는 파일이 들어왔는지 감시
FILE_PATTERN과 일치하는 파일 발견시 STDOUT 으로 파일경로 출력

## How to use
```Bash
$ python [File] [Section] [Config path]
```
- Section : 실행한 Config의 섹션
- Config path : 실행할 Config의 경로

## STDIN
없음

## STDOUT
```Bash
file://<FilePath>
```

## Configuration

**FilePatternMonitor.conf**

|Section |Option        |Range      |Description                                       |
|:------:|:------------:|-----------|--------------------------------------------------|
|GENERAL | log_path     | (string)  | log가 저장될 경로                                |
|        | LS_INTERVAL  | (int)     | 감시할 시간 간격(seconds)                        |
|Section | DIRECTORY    | (string)  | 감시할 디렉토리 경로                             |
|        | INDEX_FILE   | (string)  | 인덱스 파일 경로                                 |
|        | FILE_PATTERN | (string)  | 감시할 파일 패턴                                 |
|        | EXTEND_STR   | (string)  | 설정된 파일 패턴 끝에 추가 감시할 패턴           |
|        | FILE_SORT    | name, basename, atime, ctime, mtime | 정렬할 기준 설정       |

## Prerequisites
- Python == 2.7

## How to unit test (Dynamic test)
```Bash
$ nosetests -v --with-coverage --with-doctest --cover-erase --exe  --cover-package=. tests/*.py
```

## How to lint test (Static test)
```Bash
$ pylint --disable=C --disable=E0602 --msg-template='{path}:{line}:[{msg_id}({symbol}),{obj}]{msg}' *.py
```
