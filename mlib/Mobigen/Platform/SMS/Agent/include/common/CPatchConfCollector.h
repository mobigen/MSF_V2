


#ifndef __CPATCHCONFCOLLECTOR_H__
#define __CPATCHCONFCOLLECTOR_H__ 1

#include "CCollector.h"

//! OS(Kernel) Patch 정보를 수집하는 클래스.

class CPatchConfCollector:public CCollector
{
	public:
		/** 생성자 */
		CPatchConfCollector();
		/** 소멸자 */
		~CPatchConfCollector();
		/**
		 * OS Patch 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();
		/**
		 *	수집된 OS Patch 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();
		/**
		 *	장애 판단을 위한 메쏘드. 현재 사용되지 않음.
		 */
		void isOverThreshold(CItemCondition *cond){};

	private:
		scCoreView *m_coreview;		/**< system kernel 정보를 조회하기 위한 kernel core 변수 */
		scSysPatchInfo *m_patch;	/**< OS Patch 정보 조회 변수 */
		v_list_t *m_list;			/**< system에 설치된 os patch 개수만큼 scSysPatchInfo 정보를 저장하는 리스트 */
};

#endif /* __CPATCHCONFCOLLECTOR_H__ */
