


#ifndef __CMEMORYPERFCOLLECTOR_H__
#define __CMEMORYPERFCOLLECTOR_H__ 1

#include "CCollector.h"


//! 메모리 성능 정보를 수집하는 클래스.
/**
 *	물리적 메모리(Total Memory size(MB), Free Memory(MB), Memory usage(%)),
 *	Swap 메로리(Total Swap Memory size(MB), Free Swap Memory size(MB), Swap Memory Usage(%)),
 *	페이지 스캔, 페이지 아웃, 스왑 아웃 정보를 수집하는 클래스.
 */
class CMemoryPerfCollector:public CCollector
{
	public:
		/** 생성자 */
		CMemoryPerfCollector();
		/** 소멸자 */
		~CMemoryPerfCollector();
		/**
		 * 메모리 성능 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();
		/**
		 *	수집된 메모리 성능 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();
		/**
		 *	장애 판단을 위한 메쏘드. 현재 사용되지 않음.
		 */
		void isOverThreshold(CItemCondition *cond);

		/**
		 *	Memory 성능 임계치 장애를 발생시키는 메쏘드.
		 *	임계치를 초과한 경우에는 장애를 발생시키고, 
		 *	이전에 장애가 발생한 적이 있고, 임계치를 초과하지 않은 경우에는 장애를 해지시킨다.
		 *
		 *	@param CItemCondition pointer.
		 *	@param character CPU name.
		 *	@param 성능 임계치 초과 여부. 임계치를 넘은 경우는 true, 초과하지 않은 경우 false.
		 */
		void checkAlarm(CItemCondition *cond, char *instname, bool b);


	private:
		scCoreView *m_coreview;	/**< system kernel 정보를 조회하기 위한 kernel core 변수 */
		scMemStatus m_memstat;	/**< 메모리 상태 정보를 조회하기 위한 변수 */
		scVMStatus m_vmstat;	/**< Virtual Memory 상태 정보를 조회하기 위한 변수 */
};

#endif /* __CMEMORYPERFCOLLECTOR_H__ */
