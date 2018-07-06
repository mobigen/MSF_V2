# bin

## Aggregator
CSV -> Aggregation -> DB


## FilePatternMonitor
Monitoring files in directory -> STDOUT

디렉토리 안에 Config에서 설정한 파일이 존재하는지 확인하여 해당 경로를 STDOUT으로 출력하는 모듈

## HdfsLoader
Local to HDFS

Local경로에 있는 파일을 HDFS로 적재하는 일을 합니다. 자바로 구현되어 있습니다.

## HiveLoader
HDFS to Hive

HDFS에 있는 파일을 Hive로 적재시키는 일을 합니다.

## IrisLoader
.dat to IRIS

준비되어있는 DAT(아이리스에 로드할 데이터파일)과 CTL(아이리스에 로드할 컬럼정의파일)을

이용하여 지정된 IRIS서버로 로드합니다.

## IrisSplitter
.csv to .dat and .ctl for loading to IRIS

단순한 CSV파일을 Iris에 로드하기 위해서는 파티션별로 따로 구분하여 각각 DAT 파일을 생성해야 합니다.

본 모듈은 Config에 지정된 설정에 따라 파티션별로 DAT 파일을 생성하게 됩니다.

## IrisSummary
쿼리를 실행하여 stdin으로 입력받은 data파일의 시간에 대한 summary

## KafkaModules
Producer, Consumer python 모듈

Producer가 쿼리를 통해 DB에서 결과를 받고 카프카 브로커 서버로 전송합니다.

MessageMonitor는 카프카 브로커 서버에서 받은 데이터를 바탕으로 csv 파일로 덤프하게 됩니다.

## LoadManager
DB to DB

Source DB에서 쿼리문을 입력한 결과를 Destination DB로 로드합니다.

## MySQLHandler
MySQLHandling class

MySQL을 다루기 위한 클래스입니다.

## SFTPCollector
Remote files -> (SFTP) -> Local

FTP 프로토콜을 통해 원격지에 있는 디렉토리를 감시해 갱신된 파일을 로컬 디렉토리로 가져옵니다.

## SSHTailCollector
Remote files -> (SSH, tail명령어) -> Local

SSH 프로토콜을 통해 원격지의 파일을 줄 단위마다 감시하여 로컬에 있는 파일로 수집하게됩니다.

## Scheduler
Crontab과 기능 동일합니다.
