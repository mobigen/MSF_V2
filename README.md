# MSF_V2

## SMS-master
Iris/System등의 Resource를 확인하여 Email/SMS 전송 라이브러리
Cron을 사용하여 스케쥴링한다.

## bin
단일 공통 모듈 저장소

### Aggregator
CSV -> Aggregation -> DB

### FilePatternMonitor
Monitoring files in directory -> STDOUT

### HdfsLoader
Local to HDFS

### HiveLoader
HDFS to Hive

### IrisLoader
.dat to IRIS

### IrisSplitter
.csv to .dat and .ctl for loading to IRIS

### IrisSummary
쿼리를 실행하여 stdin으로 입력받은 data파일의 시간에 대한 summary

### KafkaModules
Producer, Consumer python 모듈

### LoadManager
DB to DB

### MySQLHandler
MySQLHandling class

### SFTPCollector
Remote files -> (SFTP) -> Local

### SSHTailCollector
Remote files -> (SSH, tail명령어) -> Local

### Scheduler
Crontab과 기능 동일

## mlib
모비젠 공통 모듈 저장소

