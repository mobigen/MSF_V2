060724-DataContainer2 문서작성

put
  - self.fdData, self.fdIdx
    이 두 fd 는 이미 현재 포인트를 가리키고 있다고 가정
  - self.recNo, self.dataOffset
    이 두값은 이미 셋팅되어 있다고 가정
  - 데이터 파일에 데이터 쓰기
  - 인덱스 파일에 인덱스 쓰기

get
  - getIdx : 인덱스 파일 읽어오기
    - 주어진 key 값이 존재하는지 idxFile 의 길이로 먼저 판단
    - nextIdx : 현재 fd 이후의 인덱스 파일 읽어오기


--- 자동복구의 범위
아래 원칙에 따라 DB 에 기록이 된다.
  - 쓰기 : 반드시 DB 파일부터 쓰고 인덱스를 쓴다. 
           그러므로 인덱스 레코드가 완전하면 그에 해당하는 DB 레코드는 완전하다.
  - 읽기 : 완전한 인덱스 레코드까지만 읽고, 거기에 해당하는 데이터를 읽는다.

위 원칙에 따라 쓰는 쪽에서 비정상 종료시는 다음 3가지만 존재한다.

1. 데이터를 불완전하게 쓰고 인덱스를 쓰지 못했다.
2. 데이터를 완전하게   쓰고 인덱스를 쓰지 못했다.
3. 데이터를 완전하게   쓰고 인덱스를 불완전하게 썼다.

위 3가지 경우 아래와 같이 자동복구한다.
  - 쓰기 : 완전한 인덱스를 기준으로 복구해서 쓴다.
  - 읽기 : 완전한 인덱스를 기준으로 읽으므로 다음 완전한 데이터가 쓰일때 까지 기다린다.

아래 장애 상황은 사람이 인위적으로 DB 파일을 건드려 발생하는 장애이다.
1. 완전한 인덱스 레코드가 존재함에도 불구하고 거기에 해당하는 데이터 레코드가 불완전할경우
  - 쓰기 : 최초 데이터 레코드를 읽는중에 바디가 아직 미완성으로 판단하고 블럭되어 버린다. -> 수동복구필요
  - 읽기 : 다음 데이터 레코드를 읽는중에 바디가 아직 미완성으로 판단하고 블럭되어 버린다. -> 수동복구필요

writer 가 2개가 동작했을경우는 fcntl 의 file lock 으로 방지했다.
  - 두번째 쓰기 프로세스가 블럭된다. -> 강제종료 필요

인서트 성능
testDataLogWriter.py
BufSize = 100
80byte 데이터 10만게 인서트시 2.25초

w,a 모드일 경우 반드시 마지막에 close 를 해 주어야 한다.
BufSize 를 지정해 놓고 close 를 하지 않으면 버퍼링 된 데이터가 들어가지 않는다.

msgTime 기준 파일 스위치 원칙
  - 원시데이터 인서트시 msgTime 을 기준으로 파일을 분리해서 저장한다.
  - msgTime 은 항상 같거나 증가하는 원칙을 지켜야 한다.
  - msgTime 을 기준으로 1시간이 지나면 파일을 스위치 하는데 일단 스위치 되면
    그 파일보다 과거 데이터가 들어오더라도 현재 파일에 저장된다.
  - 1시간 단위 파일 기준으로 현재 데이터보다 미래 데이터가 나오면 그 msgTime 기준으로
    파일을 스위치 한다.
  - 위의 경우 잘못된 데이터로 매우 미래의 파일이 만들어 지면 그 이후의 데이터들은 모두
    그 파일로 입력되는 오류가 있어 FileTimeInterval 이란 옵션을 주어서 시간단위로
    일정 시간 이후의 데이터가 들어오면 error.log 파일에 별도 저장하고 무시하도록 한다.

--- DataContainer 테스트

* 인서트 시험

testDataConPut.py testDataCon 2 240
  - testDataCon 디렉토리에서 파일 생성 확인
  - 20050801000000 부터 2일간의 48개 파일 생성

* 인서트된 데이터 확인 시험

testDataConGet.py testDataCon
  * fileTime(20050801000000) = 20050801000000
  * key(0) = 0
  curFileTime, msgTime, opt, key, value = 20050801000000, 20050801000000, opt, 0, val
  * fileTime(20050801000000) = 20050802000000
  * key(0) = 1
  curFileTime, msgTime, opt, key, value = 20050802000000, 20050802000001, opt, 1, val

* append 시험

testDataConAppend.py testDataCon 2 240
  - testDataCon 디렉토리에서 파일 추가 확인
  - 20050803000000 부터 2일간의 데이터가 추가되어 48 * 2 의 파일 생성

* 데이터 인서트 도중 msgTime 이 잘못된 데이터 시험

testDataConPutFTI.py testDataCon 2 240
  - vi ./testDataCon/error.log 확인
  - 3000 년도 데이터 들어가 있음

* 시간을 키값으로 데이터를 검색하는 시험

testDataConGetByTime.py testDataCon
* fileTime(20050802000000) = 20050802000000
* msgTime(20050802010101) = 20050802005958
curFileTime, msgTime, opt, key, value = 20050802000000, 20050802005958, opt, 3598, val
* fileTime(20050802000000) = 20050802000000
* msgTime(20050802010101) = 20050802005959
curFileTime, msgTime, opt, key, value = 20050802000000, 20050802005959, opt, 3599, val
* fileTime(20050802000000) = 20050802000000
* msgTime(20050802010101) = 20050802010101
curFileTime, msgTime, opt, key, value = 20050802000000, 20050802005959, opt, 3599, val

* option 을 키값으로 데이터를 검색하는 시험
  - 시간을 키값으로 시험하는 것과 동일
  - option field 는 left space padding 이므로 이를 고려하여 소팅된다고 보면 된다.


* 시간을 키값으로 데이터를 검색한 다음 그다음 10개 레코드를 next 메써드로 가져오는 시험
testDataConGetByTimeAndNext.py testDataCon

* fileTime(20050802000000) = 20050802000000
* msgTime(20050802005950) = 20050802005955
* prnCnt(10) = 10
curFileTime, msgTime, opt, key, value = 20050802000000, 20050802005955,              opt, 3595, val
curFileTime, msgTime, opt, key, value = 20050802000000, 20050802005956,              opt, 3596, val
curFileTime, msgTime, opt, key, value = 20050802000000, 20050802005957,              opt, 3597, val
curFileTime, msgTime, opt, key, value = 20050802000000, 20050802005958,              opt, 3598, val
curFileTime, msgTime, opt, key, value = 20050802000000, 20050802005959,              opt, 3599, val
curFileTime, msgTime, opt, key, value = 20050802010000, 20050802010000,              opt, 0, val
curFileTime, msgTime, opt, key, value = 20050802010000, 20050802010001,              opt, 1, val
curFileTime, msgTime, opt, key, value = 20050802010000, 20050802010002,              opt, 2, val
curFileTime, msgTime, opt, key, value = 20050802010000, 20050802010003,              opt, 3, val
curFileTime, msgTime, opt, key, value = 20050802010000, 20050802010004,              opt, 4, val


데이터 put 방법

데이터 append 방법

데이터 get 방법

데이터 next 방법
  - get 을 수행한 다음 next 를 수행하면 get 을 수행한 다음 레코드부터 가져온다.
  - get 을 수행하지 않고 next 를 수행하면 가장 최근파일의 가장 최근 레코드부터 가져온다.

