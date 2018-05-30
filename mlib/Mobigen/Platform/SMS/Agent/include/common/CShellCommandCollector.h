


#ifndef __CSHELLCOMMANDCOLLECTOR_H__
#define __CSHELLCOMMANDCOLLECTOR_H__ 1

#include "CCollector.h"

//! shell command를 수행한 결과값을 수집하는 클래스.

class CShellCommandCollector:public CCollector
{
	public:
		/** 생성자 */
		CShellCommandCollector();
		/** 소멸자 */
		~CShellCommandCollector();
		/**
		 * Shell command 명령을 수행한 결과값을 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();
		/**
		 *	수집된 Shell command 명령을 수행한 결과값을 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();
		/**
		 *	장애 판단을 위한 메쏘드. 현재 사용되지 않음.
		 */
		void isOverThreshold(CItemCondition *cond){};

	private:
		scCoreView *m_coreview;	/**< system kernel 정보를 조회하기 위한 kernel core 변수 */
		char *m_result;	/**< Shell command 수행 결과값 */
};

#endif /* __CSHELLCOMMANDCOLLECTOR_H__ */
