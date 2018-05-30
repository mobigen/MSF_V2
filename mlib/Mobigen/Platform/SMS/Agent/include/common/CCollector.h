

#ifndef __CCOLLECTOR_H__
#define __CCOLLECTOR_H__

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <unistd.h>
#include <errno.h>

#include "CMisc.h"

#include "CAgentEnvVar.h"
#include "CPolicyItem.h"


//! 정보 수집 클래스
/**
 *	모든 정보 수집기는 이 클래스를 상속하여 구현된다.
 */
class CCollector
{
	public:
		/** 생성자 */
		CCollector();
		/** 소멸자 */
		virtual ~CCollector(){};
		/**
		 *	정보 수집 쓰레드(SCThread)에 의해 정보 수집을 요청하는 메쏘드
		 *	@see SCThread
		 */
		virtual void collect(){};
		/**
		 *	수집된 정보를 SMS Manager로 전송하기 위한 규약된 메시지 포맷으로 변환하는 메쏘드.
		 */
		virtual void makeMessage(){};
		/**
		 *	수집된 정보가 임계치(CItemCondition)에 위배 되는지 여부를 판단하여 장애를 발생시키는 메쏘드.
		 *	@see CItemCondition, CAalarmProcessor
		 */
		virtual void isOverThreshold(CItemCondition *cond) {};
		/**
		 *	정보 수집 정책 클래스(CPolicyItem)를 설정하는 메쏘드.
		 *	@param 정보 수집 정책 클래스.
		 *	@see CPolicyItem
		 */
		void setPolicyItem(CPolicyItem *pollitem){ m_pollitem = pollitem; }
		/**
		 *	수집 정책 정보를 얻어오기 위한 메쏘드
		 *	@return CPolicyItem pointer.
		 */
		CPolicyItem *getPolicyItem(){ return m_pollitem; }
		/**
		 *	SMS Agent 환경 정보를 관리하는 클래스를 설정하는 메쏘드
		 *	@param CAgentEnvVar pointer
		 *	@see CAgentEnvVar
		 */
		void setEnvVar(CAgentEnvVar *envvar){ m_envvar = envvar; }
		/**
		 *	SMS Agent 환경 정보를 관리하는 클래스를 얻어오는 메쏘드
		 *	@return CAgentEnvVar pointer
		 *	@see CAgentEnvVar
		 */
		CAgentEnvVar *getEnvVar(){ return m_envvar; }
		/**
		 *	수집 정책이 단기 수집인지 여부를 판단하는 메쏘드
		 *	@return true if short period, else return false
		 */
		bool isShortPerf();

	protected:
		CAgentEnvVar *m_envvar;		/**< SMS Agent 환경 정보를 관리하는 클래스 */
		CPolicyItem *m_pollitem;	/**< 수집 정책 */
		CMessageFormatter m_msgfmt;	/**< 메시지 변환기 */
};

#endif /* __CCOLLECTOR_H__ */

