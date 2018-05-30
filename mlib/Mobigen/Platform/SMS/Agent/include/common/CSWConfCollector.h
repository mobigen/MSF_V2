


#ifndef __CSWCONFCOLLECTOR_H__
#define __CSWCONFCOLLECTOR_H__ 1

#include "CCollector.h"

//! 시스템에 설치된 S/W(Application) 정보를 수집하는 클래스.
class CSWConfCollector:public CCollector
{
	public:
		/** 생성자 */
		CSWConfCollector();
		/** 소멸자 */
		~CSWConfCollector();
		/**
		 * 시스템에 설치된 S/W(Application) 구성 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();
		/**
		 *	수집된 시스템에 설치된 S/W(Application) 구성 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();
		/**
		 *	장애 판단을 위한 메쏘드. 현재 사용되지 않음.
		 */
		void isOverThreshold(CItemCondition *cond){};

	private:
		scCoreView *m_coreview;		/**< system kernel 정보를 조회하기 위한 kernel core 변수 */
		scSysPkgInfo *m_pkg;		/**< S/W 정보를 조회하기 위한 변수 */
		v_list_t *m_list;			/**< 시스템에 설치된 S/W 정보를 저장하기 위한 리스트 */
};

#endif /* __CSWCONFCOLLECTOR_H__ */
