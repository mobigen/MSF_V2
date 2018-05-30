
#ifndef _CAGENTENVVAR_H__
#define _CAGENTENVVAR_H__

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <string>

#include "CAgentConfigVar.h"
#include "CQueue.h"
#include "CKernelCore.h"

#if defined(ORACLE_ENABLE)
#include "CDBPool.h"
#endif /* ORACLE_ENABLE */


//! SMS Agent가 기동하면서 필요한 모든 환경 설정 정보 및 item 정보를 관리하는 클래스
/**
 *	system kernel 정보를 조회하기 위한 인터페이스(CKernelCore)\n
 *	item code 정보를 관리하는 인터페이스(CAgentConfigVar)\n
 *	SMS Agent 내부적으로 데이터를 주고받기 위한 각종 메시지 큐\n
 *	SMS Agent session 상태 정보\n
 *	Database session pool 정보 등을 관리한다.
 *	@see CKernelCore, CAgentConfig, CDBPool.
 */
class CAgentEnvVar 
{
	public :
		/**
		 *	생성자
		 *	각종 변수를 초기화한다.
		 */
		CAgentEnvVar(){
			m_kernel = new CKernelCore;
			m_configVar = new CAgentConfigVar;
			m_eventQ = new CQueue;
			m_shortPerfQ = new CQueue;
			m_longPerfQ = new CQueue;
			m_respQ = new CQueue;
			m_cmdQ = new CQueue;
			m_policyQ = new CQueue;
#if defined(ORACLE_ENABLE)
			m_dbpool = new CDBPool;
#endif /* ORACLE_ENABLE */
			m_session_event = false;
			m_session_shortperf = false;
			m_session_longperf = false;
			m_session_resp = false;
			m_session_cmd = false;
		}
		/** 소멸자 */
		~CAgentEnvVar(){
			delete m_configVar;
			delete m_eventQ;
			delete m_shortPerfQ;
			delete m_longPerfQ;
			delete m_respQ;
			delete m_cmdQ;
			delete m_policyQ;
			delete m_kernel;
#if defined(ORACLE_ENABLE)
			delete m_dbpool;
#endif /* ORACLE_ENABLE */
		}
		/**
		 *	수집기와 Event 메시지 처리 소켓 쓰레드와 통신한기 위한 메시지 큐를 얻어오는 메쏘드.
		 *	@return Event(Alarm) message Queue.
		 */
		CQueue *getEventQ(){ return m_eventQ; }
		/**
		 *	수집기와 단기 성능 메시지 처리 소켓 쓰레드와 통신한기 위한 메시지 큐를 얻어오는 메쏘드.
		 *	@return 단기 성능 message Queue.
		 */
		CQueue *getShortPerfQ(){ return m_shortPerfQ; }
		/**
		 *	수집기와 중장기 성능 메시지 처리 소켓 쓰레드와 통신한기 위한 메시지 큐를 얻어오는 메쏘드.
		 *	@return 중장기 성능 message Queue.
		 */
		CQueue *getLongPerfQ(){ return m_longPerfQ; }
		/**
		 *	수집기와 명령 응답 메시지 처리 소켓 쓰레드와 통신한기 위한 메시지 큐를 얻어오는 메쏘드.
		 *	@return 명령 응담 message Queue.
		 */
		CQueue *getRespQ(){ return m_respQ; }
		/**
		 *	명령어 처리기(CProtocolProcessor)와 명령 코드 처리 소켓 쓰레드(CSocketWorkerThread)와 통신한기 위한 메시지 큐를 얻어오는 메쏘드.
		 *	@return 명령 메시지 Queue.
		 *	@see CProtocolProcessor, CSocketWorkerThread, CQueue.
		 */
		CQueue *getCmdQ(){ return m_cmdQ; }
		/**
		 *	스케쥴러(CScheduler)와 정보 수집 쓰레드(SCThread)와 통신한기 위한 정책 큐를 얻어오는 메쏘드.
		 *	@return 수집 정책 Queue.
		 *	@see CScheduler, SCThread, CPolicyItem, CQueue
		 */
		CQueue *getPolicyQ(){ return m_policyQ; }
		/**
		 *	system kernel core interface class(CKernelCore)를 얻어오기 위한 메쏘드.
		 *	@return CKernelCore pointer.
		 *	@see CKernelCore
		 */
		CKernelCore *getKernelCore(){ return m_kernel; }
		/**
		 *	item code 정보를 관리하는 클래스(CAgentConfigVar)를 얻어오기 위한 메쏘드.
		 *	@return CAgentConfigVar pointer.
		 *	@see CAgentConfigVar
		 */
		CAgentConfigVar *getAgentConfigVar() { return m_configVar; }
#if defined(ORACLE_ENABLE)
		/**
		 *	ORACLE Database session pool을 관리하는 클래스(CDBPool)를 얻어오기 위한 메쏘드.
		 *	@return CDBPool pointer
		 *	@see CDBPool, CDBSession
		 */
		CDBPool *getDBPool() { return m_dbpool; }
#endif /* ORACLE_ENABLE */
		/**
		 *	SMS Agent와 SMS Manager간의 장애 소켓 세션 상태 정보를 얻어오는 메쏘드.
		 *	@return session status pointer.
		 */
		bool *getEventSession(){ return &m_session_event; }
		/**
		 *	SMS Agent와 SMS Manager간의 단기 성능 소켓 세션 상태 정보를 얻어오는 메쏘드.
		 *	@return session status pointer.
		 */
		bool *getShortPerfSession(){ return &m_session_shortperf; }
		/**
		 *	SMS Agent와 SMS Manager간의 중장기 소켓 세션 상태 정보를 얻어오는 메쏘드.
		 *	@return session status pointer.
		 */
		bool *getLongPerfSession(){ return &m_session_longperf; }
		/**
		 *	SMS Agent와 SMS Manager간의 명령 응답 소켓 세션 상태 정보를 얻어오는 메쏘드.
		 *	@return session status pointer.
		 */
		bool *getRespSession(){ return &m_session_resp; }
		/**
		 *	SMS Agent와 SMS Manager간의 명령어 처리 소켓 세션 상태 정보를 얻어오는 메쏘드.
		 *	@return session status pointer.
		 */
		bool *getCmdSession(){ return &m_session_cmd; }

	private :
		CKernelCore *m_kernel;			/**< system kernel interface class */
		CAgentConfigVar *m_configVar;	/**< item code 정보를 관리하는 클래스 */
		CQueue *m_eventQ;				/**< 장애 메시지 큐 */
		CQueue *m_shortPerfQ;			/**< 단기 성능 메시지 큐 */
		CQueue *m_longPerfQ;			/**< 중장기 성능 메시지 큐 */
		CQueue *m_respQ;				/**< 명령어 응답 메시지 큐 */
		CQueue *m_cmdQ;					/**< 명령어 큐 */
		CQueue *m_policyQ;				/**< 수집 정책 정보 큐 */
#if defined(ORACLE_ENABLE)
		CDBPool *m_dbpool;				/**< Database session pool */
#endif /* ORACLE_ENABLE */
		bool m_session_event;			/**< 장애 세션 상태 */
		bool m_session_shortperf;		/**< 단기 성능 세션 상태 */
		bool m_session_longperf;		/**< 중장기 성능 세션 상태 */
		bool m_session_resp;			/**< 명령 응답 세션 상태 */
		bool m_session_cmd;				/**< 명령 세션 상태 */
};

#endif /* _CAGENTENVVAR_H__ */
