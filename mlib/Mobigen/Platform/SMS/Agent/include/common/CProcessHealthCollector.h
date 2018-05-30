


#ifndef __CPROCESSHEALTHCOLLECTOR_H__
#define __CPROCESSHEALTHCOLLECTOR_H__ 1

#include "CCollector.h"


//! 프로세스 구동 상태 여부 정보를 수집하는 클래스
/**
 *	프로세스 이름, 현재 상태 정보를 수집하여 전송한다.
 */
class CProcessHealthCollector:public CCollector
{
	public:
		/** 생성자 */
		CProcessHealthCollector();
		/** 소멸자 */
		~CProcessHealthCollector();
		/**
		 *	프로세스 상태 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();
		/**
		 *	수집된 프로세스 상태 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();
		/**
		 *	장애 판단을 위한 메쏘드.
		 */
		void isOverThreshold(CItemCondition *cond);

		void initInstance();

		void checkAlarm(CItemCondition *cond, scPSInfo *psinfo, bool ialarm);

	private:
		scCoreView *m_coreview;	/**< system kernel 정보를 조회하기 위한 kernel core 변수 */
		scPSInfo *m_psinfo;		/**< 개별 프로세스 상태 정보를 조회하기 위한 변수 */
		v_list_t *m_list;		/**< 시스템에 기동된 모든 프로세스 정보를 저장하는 리스트 */
		CQueue *m_procQ;		/**< process count Queue */
};

#endif /* __CPROCESSHEALTHCOLLECTOR_H__ */
