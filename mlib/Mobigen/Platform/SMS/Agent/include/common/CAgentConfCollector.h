

#ifndef __CAGENTCONFCOLLECTOR_H__
#define __CAGENTCONFCOLLECTOR_H__ 1

#include "CCollector.h"
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

class CAgentConfCollector:public CCollector
{
	public:
		/** 생성자 */
		CAgentConfCollector();
		/** 소멸자 */
		~CAgentConfCollector();
		/**
		 *	Agent Configuration 정보를 수집하는 메쏘드를 overriding한다.
		 *	Port, Oracle uid, pwd, sid 등의 정보를 수집하여 SMS Manager로 전송한다.
		 *	@see CCollector.
		 */
		void collect();
		/**
		 *	장애 판단을 위한 메쏘드. 현재 사용되지 않음.
		 */
		void isOverThreshold(CItemCondition *cond){};

		void makeMessage();
	private:
};

#endif /* __CAGENTCONFCOLLECTOR_H__ */
