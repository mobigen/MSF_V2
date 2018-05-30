


#ifndef __CMEMORYCONFCOLLECTOR_H__
#define __CMEMORYCONFCOLLECTOR_H__ 1

#include "CCollector.h"


//! 메모리 구성 정보를 수집하는 클래스.
/**
 *	Total memory size(MB), Total Swap Memory size(MB) 정보를 수집하는 클래스.
 */
class CMemoryConfCollector:public CCollector
{
	public:
		/** 생성자 */
		CMemoryConfCollector();
		/** 소멸자 */
		~CMemoryConfCollector();
		/**
		 * 메모리 구성 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();
		/**
		 *	수집된 메모리 구성 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();
		/**
		 *	장애 판단을 위한 메쏘드. 현재 사용되지 않음.
		 */
		void isOverThreshold(CItemCondition *cond){};

	private:
		scCoreView *m_coreview;	/**< system kernel 정보를 조회하기 위한 kernel core 변수 */
		scMemStatus m_mem;		/**< 메모리 구성 정보 조회 변수 */
};

#endif /* __CMEMORYCONFCOLLECTOR_H__ */
