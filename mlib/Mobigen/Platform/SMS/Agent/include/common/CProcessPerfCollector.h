


#ifndef __CPROCESSPERFCOLLECTOR_H__
#define __CPROCESSPERFCOLLECTOR_H__ 1

#include "CCollector.h"


//! 프로세스 성능 정보를 수집하는 클래스.
/**
 *	프로세스 이름, 프로세스 CPU 점유율, 프로세스 메모리 점유율 정보를 조회하는 클래스.
 */
class CProcessPerfCollector:public CCollector
{
	public:
		/** 생성자 */
		CProcessPerfCollector();
		/** 소멸자 */
		~CProcessPerfCollector();
		/**
		 *	프로세스 성능 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();
		/**
		 *	수집된 프로세스 성능 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();
		/**
		 *	장애 판단을 위한 메쏘드. 현재 사용되지 않음.
		 */
		void isOverThreshold(CItemCondition *cond);

		/**
		 *	Process 성능 임계치 장애를 발생시키는 메쏘드.
		 *	임계치를 초과한 경우에는 장애를 발생시키고, 
		 *	이전에 장애가 발생한 적이 있고, 임계치를 초과하지 않은 경우에는 장애를 해지시킨다.
		 *
		 *	@param CItemCondition pointer.
		 *	@param character CPU name.
		 *	@param 성능 임계치 초과 여부. 임계치를 넘은 경우는 true, 초과하지 않은 경우 false.
		 *	@param Process 성능 정보를 저장하고 있는 구조체.
		 */
		void checkAlarm(CItemCondition *cond, char *instname, bool b, scPSInfo *status);

	private:
		scCoreView *m_coreview;	/**< system kernel 정보를 조회하기 위한 kernel core 변수 */
		scPSInfo *m_psinfo;		/**< 개별 프로세스 성능 정보를 조회하기 위한 변수 */
		v_list_t *m_list;		/**< 시스템에 기동된 모든 프로세스 정보를 저장하는 리스트 */
};

#endif /* __CPROCESSPERFCOLLECTOR_H__ */
