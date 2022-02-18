## IRIS DB partition 관련 tool script

###  P_000_backup.py 

시간, 일, 월, year 파티션 테이블  백업하기


    ./P_000_backup.py table이름 백업디렉토리
    
### P_002_create_table_sql.py

파티션 테이블 생성하는 SQL 을 STDOUT 출력하는 스크립트 

    ./P_002_create_table_sql.py tablename partition(hour|day|month|year)
    
### P_003_execute_sql.py

테이블 생성 SQL 을 IRIS DB 에 접속하여 실행하는 스크립트 ( `.table`  명령어도 가능 )

    ./P_003_execute_sql.py ./테이블.sql
    
    
### P_004_makeCTL_loadTable.py

백업받은 테이블 데이터 파일을 재적재하는 스크립트. 이 때 ctl 파일은 DB 에 접속하여 테이블에서 가져온 정보로 자동 생성합니다.

    ./P_004_makeCTL_loadTable.py tablename data_directory
    ./P_004_makeCTL_loadTable.py tablename data_directory [partition_key]
    
### N_005_make_sql_table.py

헤더가 있는 csv 데이터 파일에서 create table SQL 생성하기

    ./N_005_make_sql_table.py tablename data_filename fld_seperator  > ./tablename.sql
    
### N_004_load_NO_partition_local.py

csv 데이터 파일을 IRIS DB 테이블(미리 생성되어 있어야 함)에 로딩하는 스크립트
첫라인이 header 인 경우에는  -header  인자를 추가합니다.

    ./N_004_load_NO_partition_local.py tablename data_directory [-header]
    
    
### P_001_merge_by_YEAR.py

year 파티션은 'YYYY0101000000' 으로 partition 기준 컬럼의 값을 통일해야 합니다.
백업받은 파일에서 파티션 기준 컬럼을 자동으로 year 파티션 값으로 변경해서 파일을 merge  하는 스크립트 입니다.


    ./P_001_merge_by_YEAR.py table이름 백업디렉토리 year_merge파일디렉토리


