

#ifndef __CLOGCHECKCOLLECTOR_H__
#define __CLOGCHECKCOLLECTOR_H__ 1

#include "CCollector.h"
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

/**
 *	로그 파일의 instance명 및 해당 인스턴스의 실제 파일 정보를 저장하는 구조체.
 */
typedef struct _st_loginst {
	char instance[256];
	char fmt_instance[256];
	struct stat sbuf;
}st_loginst;

//! 로그 파일의 내용을 수집하여 보고하는 클래스.
/**
 *	로그 파일명(instance name)은 일반 파일 및 다음과 같은 포맷의 파일 형태가 올 수 있다.
 *	%Y : 4자리 년도.
 *	%y : 2자리 년도.
 *	%m : 2자리 월.
 *	%d : 2자리 일.
 *	%H : 2자리 시간.
 *	%M : 2자리 분.
 *	%S : 2자리 초.
 *	ex) instance가 "logfile_%Y-%m-%d"라면, 실제 파일명은 "logfile_2006-04-25"로 변경된다.
 */
class CLogCheckCollector:public CCollector
{
	public:
		/** 생성자 */
		CLogCheckCollector();
		/** 소멸자 */
		~CLogCheckCollector();
		/**
		 *	로그 정보를 수집하는 메쏘드. CCollector 클래스의 메쏘드를 overriding한다.
		 *	@see CCollector.
		 */
		void collect();
		/**
		 *	실제 로그 정보를 수집하는 메쏘드.
		 */
		void collectLog();
		/**
		 *	등록된 인스턴스(로그 파일) 개별로 로그 정보를 수집하는 메쏘드.
		 *	처음 기동시에는 정보를 수집하지 않고, 두 번째 수집 주기부터, 발생하는 로그 정보를 수집하여,
		 *	CItemCondition에 등록된 장애 발생 조건과 비교하여 event를 발생시킨다.
		 *	@param 로그 파일(instance) 정보.
		 */
		void collectLogInstance(st_loginst *loginst);
		/**
		 *	시간 정보가 변경되어 로그 파일명이 새로운 시간으로 새로 생긴 경우에 이를 확인하기 위한 메쏘드.
		 *	예를 들어 Instace가 "log.%Y-%m-%d"로 등록되어 이전까지 "log.2006-04-20"파일의 정보를 수집하다가,
		 *	시스템의 현재 시간이 2006년 4월 21일로 바뀐 경우는 "log.2006-04-21"파일로 변경되었기 때문에 이에 대한 확인이 필요한다.
		 */
		void checkFmtInstance();
		/**
		 *	변경된 새로운 로그 파일명으로 설정하는 메쏘드.
		 */
		void setFmtInstance();
		/**
		 *	주어진 문자열의 내용이 장애 발생 조건식(CItemCondition)을 만족하는지 여부를 판단하고,
		 *	장애를 발생시키는 메쏘드.
		 *	@param 로그 파일 정보(instance).
		 *	@param 로그 내용(문자열).
		 */
		void checkCondition(st_loginst *loginst, char *log);
		/**
		 *	장애 메시지를 생성하여 장애 메시지 버퍼로 전송하는 메쏘드.
		 *	@param 장애 판단 조건 정보를 관리하는 CItemCondition pointer.
		 *	@param 로그 파일 정보(Instance).
		 *	@param 로그 내용(문자열).
		 */
		void sendEvent(CItemCondition *cond, st_loginst *loginst, char *log);
		/**
		 *	수집된 로그 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();
		/**
		 *	로그 파일의 상세 정보를 조회하여 설정하는 메쏘드.
		 *	@param 로그 파일 정보(Instance).
		 *	@param 로그 처음 수집 여부. true : 처음 기동하여 로그를 수집, false : 이전에 로그를 수집한 적이 있음.
		 */
		void setLogFileInfo(st_loginst *loginst, bool b);
		/** 장애 임계치 판단을 하는 메쏘드. 본 클래스에서는 의미없음. */
		void isOverThreshold(CItemCondition *cond){};

	private:
		CQueue m_instq;		/**< 인스턴스(로그파일) 리스트 */
};

#endif /* __CLOGCHECKCOLLECTOR_H__ */
