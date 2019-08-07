# ExecuteScrpit 참고

https://community.hortonworks.com/articles/75032/executescript-cookbook-part-1.html
https://community.hortonworks.com/articles/75545/executescript-cookbook-part-2.html
https://community.hortonworks.com/articles/77739/executescript-cookbook-part-3.html

# Jython script modules
NiFi에 기본적으로 제공되는 기능들로 구성하기 힘들거나 불가능한 요구사항을 처리하기 위한 모듈.

각 모듈 디렉토리에 예제 NiFi Template 첨부. NiFi에서 Template 호츌하여 예제 확인 가능.

## Module
### IrisSplitter
csv 형식의 파일을 지정한 key와 partition 컬럼에 따라 분리

### IrisLoader
csv 형식의 파일을 Iris에 로드

### IrisSummary
Iris는 Local테이블끼리의 조인연산을 제공하지 않음. Iris에서 Local테이블끼리의 Join 및 Union 연산을 하기위한 모듈

## Common Config
각 모듈들을 실행시키는데 필요한 공통 Config를 **common_info.py** 에 명시

- iris_conn
아이리스 접속하는데 필요한 정보
  - ip : 아이리스 접속 IP
  - port : 아이리스 접속 포트
  - user : 아이리스 접속 유저이름
  - pwd : 아이리스 접속 패스워드
  - db : 아이리스 접속 DB
  - timeout : 아이리스 결과 응답 timeout
  - direct : Direct 유무 (True or False)

- log_info
logging 옵션 정보
  - formatter : Formatter 형식 기술
  - log_dir : log가 저장되 디렉토리
  - mode : 공식 홈페이지 설명 참조 통상적으로 'a' 가 사용됨
  - maxBytes : 로그파일의 최대 바이트수
  - backupCount : 로그파일의 최대 생성 갯수
