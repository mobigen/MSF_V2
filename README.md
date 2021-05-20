# MSF_V2
SI업무하는데 필요한 모비젠의 라이브러리들을 정리합니다.

추가적으로 필요하며 범용적으로 쓰일 수 있는 기술은 WIKI에 기술합니다.

## SMS-master
Iris, System등의 Resource를 확인하여 Email/SMS 전송 라이브러리

Cron을 사용하여 스케쥴링해서 쓰는 라이브러리입니다.

실시간 Resource monitoring은 아닙니다.

## bin
SI 업무를 하는데 필요한 단일 모듈들을 정리해놓은 디렉토리입니다.

주로 수집, 파싱, 적재 역할을 담당하는 모듈들이 있습니다.

## Nifi/bin
SI 업무를 하는데 필요한 단일 모듈들을 정리해놓은 디렉토리입니다.(Nifi용)  
### 공통
#### NifiSubprocess.py 
- python 모듈을 subprocess로 실행시켜 주는 모듈
#### CommonNifi.py  
- 공통 기능들이 있는 모듈 (config 정보, 수집 정보 GET ...)
#### CommonDB.py  
- 여러 DB를 핸들링 할 수 있는 공통 모듈
#### 
### 수집
#### GetCollectInfo.py  
### 파싱
####
#### IrisSplitter.py
### 로딩
#### HdfsLoader.py
#### IrisLoader.py
#### 

## mlib
모비젠 공통 모듈 저장소 입니다.

EventFlow, M6 API 등등의 모듈들이 있습니다.


## Crawler
Python으로 구현된 Scrapy/Selenium Request를 지원하는 크롤러 모듈입니다.
