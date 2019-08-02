# IrisSummary-NiFi
IrisSummary의 스케쥴링은 프로세서의 기본 동작 설정에서 가능합니다.

SCHEDULING탭의 Scheduling Starategy를 CRON driven으로 변경 후 원하시는 스케쥴링 옵션을 Run Schedule에 입력하여 사용하십시오.

Property의 옵션 값들은 NiFi Expression Language가 적용되어 동적으로 활용이 가능합니다.

## IrisSummaryByEmbededScheduling의 필수 Property 목록
- **field_sep** : Summary된 결과의 필드 구분자 지정
- **log_suffix** : log 이름은 `<ProcessName>-<Suffix>.log.<number>` 로  되는데 여기서 suffix를 지정
- **save_path** : Summary된 결과의 저장 경로 지정 (Expression Language 지원)
- **query** :  Summary할 쿼리문 입력 (SELECT, FROM, LEFT OUTET JOIN, INNER JOIN, UNION)만 지원, 문법은 MySQL 문법과 동일하지만 MySQL은 UNION이 JOIN보다 후순위 연산임을 인식하지만 본 모듈은 JOIN및 UNION 문법을 순차적으로 적용.
- **[Table Nickname]** : Value에는 Iris 쿼리문을 입력 한 후 결과를 Property Name에 지정 Property Name은 바로 위의 **query**에 쓰일 테이블명이 됨.(Expression Language 지원)
