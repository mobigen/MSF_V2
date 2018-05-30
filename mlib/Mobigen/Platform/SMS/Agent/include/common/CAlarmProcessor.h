
#ifndef __CALARMPROCESSOR_H__
#define __CALARMPROCESSOR_H__ 1

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string>

#include "CCollector.h"

//! 수집된 정보를 이용하여 장애 처리를 담당하는 클래스
class CAlarmProcessor
{
	public:
		/** 생성자 */
		CAlarmProcessor(){};
		/**
		 *	생성자
		 *	@param CCollector pointer
		 */
		CAlarmProcessor(CCollector *collector){ m_collector = collector; }
		/**	소멸자 */
		~CAlarmProcessor(){};
		/**	임계치 장애를 판단하는 메쏘드 */
		void check();
		/**
		 *	수집기(CCollector)에서 수집한 데이터와 CItemCondition에 설정된 임계치 조건식을 분석하여
		 *	장애를 발생시키는 메쏘드.
		 *	@param CItemCondition pointer.
		 *	@see CItemCondition, CCollector
		 */
		void checkAlarm(CItemCondition *cond);

	private:
		CCollector *m_collector; /**< 정보 수집기 */
};

#endif /* __CALARMPROCESSOR_H__ */
