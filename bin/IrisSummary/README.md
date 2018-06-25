# IrisSummary

Xml로 정의된 쿼리를 파싱하고, 파싱된 쿼리를 IRIS에 실행하여 결과를 csv 파일로 저장
Stdin 으로 입력받은 data파일의 시간에 대한 summary

## How to use
```Bash
$ python IrisSummary.py <SUMMARY_NAME> <XML_FILE_PATH> <OUTPUT_DIR_PATH>
```

## STDIN
```Bash
noti://<YYYYmmddHHMMSS>
```

## STDOUT
```Bash
file://<저장된 파일 경로>
```

## Configuration
```
<?xml version="1.0" encoding="utf-8" ?>
<SummaryConfig>
   <Summary sourcename="META_SERVICE" termtype="0" term="1">
      <Sum_info>
         <Sumname>TB_V017_01M</Sumname>
         <Connection url="jdbc:iris://192.168.0.156:5050" user="lqmsadm" pass="lqmsadm123"></Connection> <!-- Connection string -->
         <Query type="HASH_MAIN" keys="3"><![CDATA[SELECT
                 STIME, CDATE, CTIME, TEAM_ID  , SUM(TX_BYTES) AS TX_BYTES
                 FROM META_THROUGHPUT
                 WHERE STIME = '%stime'
                    and system_type_code = 'E001'
                 GROUP BY STIME, CDATE, CTIME, TEAM_ID;]]></Query> <!-- IRIS or Oracle -->
         <Query type="HASH_SUB" keys="0" values="1,2" pos="4,5" range="10000"><![CDATA[SELECT
                bpu_ID, traffic_tx, traffic_rx
                FROM TB_V017_01M
                WHERE STIME = '%prev_stime';]]></Query> <!-- IRIS or Oracle -->
                <Query type="HASH_MAIN" keys="3"><![CDATA[SELECT
                    STIME, CDATE, CTIME, 0
                     , 0 AS TX_BYTES_OLD
                     , 0 AS RX_BYTES_OLD
                     , SUM(TX_BYTES) AS TX_BYTES
                     , SUM(RX_BYTES) AS RX_BYTES
                  FROM META_THROUGHPUT
                  WHERE STIME = '%stime' and system_type_code = 'E001' GROUP BY STIME, CDATE, CTIME;]]></Query>
                 <Query type="HASH_SUB" keys="0" values="1,2" pos="4,5" range="10000"><![CDATA[SELECT
                          bpu_ID,  traffic_tx, traffic_rx
                          FROM TB_V017_01M
                          WHERE STIME = '%prev_stime' and bpu_id = 0;]]></Query> <!-- IRIS or Oracle -->
      </Sum_info> 
   </Summary>
</SummaryConfig>
```
- Sourcename : META 테이블명
- Sum_info : 통계 구성
- Sumname : 통계 테이블명
- Connection : IRIS 접속 정보
- url : IRIS 접속 JDBC URL
- User : IRIS 접속 ID
- Pass: IRIS 접속 Password
- Query: IRIS Query문
- type Query문 형태
  - UNIQUE : 단일 Query
  - HASH_MAIN : HASH_SUB Query의 원본 Query
  - HASH_SUB : HASH_MAIN Query의 부가 정보 Query
- Keys : Query에서 Key가 되는 컬럼의 인덱스(HASH_MAIN, HASH_SUB)
- Values : Query에서 Value가 되는 컬럼의 인덱스(HASH_SUB)
- Pos : HASH_MAIN 데이터에 위치할 컬럼의 인덱스(HASH_SUB) # sub 결과와 동일한 필드의 main 결과 위치 정보
- range : IRIS 테이블 Partition Range 
- %cdate : yyyymmdd
- %ctime : hhnn
- %stime : 처리 yyyymmddhhnnss
- %prev_stime : 전주 yyyymmddhhnnss


## Prerequisites
- Python == 2.7
- Python-M6-API == 1.1

## How to unit test (Dynamic test)
```Bash
$ nosetests -v --with-coverage --with-doctest --cover-erase --exe  --cover-package=. tests/*.py
```

## How to lint (Static test)
```Bash
$ pylint --disable=C --disable=E0602 --extension-pkg-whitelist=MySQLdb,cx_Oracle --generated-members=message,code,ProgrammingError,OperationalError --msg-template='{path}:{line}:[{msg_id}({symbol}),{obj}]{msg}' *.py
```

## Example
1. 우선 Config와 일치하는 IRIS가 준비되어 있어야 합니다. 그리고 MSF_TEST_TABLE_MAIN 테이블이 있다면 지워주세요.
2. Example.sh 를 실행시키면 우선 테이블을 만들게 되고 Config의 조건에 맞는 쿼리를 실행시키게 되고 결과를 tmp 디렉토리에 생성하게 됩니다.
3. IRIS에서 생성된 테이블을 확인하고 tmp 디렉토리에 어떤 파일이 생성됬는지 확인하세요.
