
#ifndef __CSOCKETWORKERTHREADH__
#define __CSOCKETWORKERTHREADH__

#include "termio.h"
#include "CAgentEnvVar.h"
#include "CSocketWorker.h"
#include "CProtocolProcessor.h"
#include "CMisc.h"
#include "SCThreadObserver.h"


extern pthread_mutex_t g_session_lock;

#define SC_STREAM_TYPE_EVENT 1
#define SC_STREAM_TYPE_COMMAND 2
#define SC_STREAM_TYPE_SESSION 3

#define TELNET_SE               240 
#define TELNET_NOP              241 
#define TELNET_DATA_MARK        242 
#define TELNET_BRK              243 
#define TELNET_IP               244 
#define TELNET_AO               245 
#define TELNET_AYT              246 
#define TELNET_EC               247 
#define TELNET_EL               248 
#define TELNET_GA               249 
#define TELNET_SB               250 
#define TELNET_WILL             251 
#define TELNET_WONT             252 
#define TELNET_DO               253 
#define TELNET_DONT             254 
#define TELNET_IAC              255 


#define TELNET_ECHO               1 
#define TELNET_SUPPRESS_GO_AHEAD  3 


//! SMS Manager와 SMS Agent간 통신을 담당하는 클래스
class CSocketWorkerThread : public OpenThreads::Thread, public ThreadReporter, public CSocketWorker {

public:
	/**
	 *	생성자
	 *	@param SMS Agent 환경 정보 관리 클래스.
	 *	@param void data pointer.
	 *	@param 소켓 세션의 연결 유무를 설정하는 pointer.
	 *	@param element number. 의미없음.
	 *	@param 메시지 처리 타입(EVENT REPORT, ACCEPT COMMAND, SESSION STATUS REPORT)
	 */
    CSocketWorkerThread(CAgentEnvVar *envvar, void *_data, bool *_session, int port, int numElts, int type) : OpenThreads::Thread(), ThreadReporter(),
        m_envvar(envvar), m_data(_data), m_session_status(_session), m_port(port), _numElts(numElts), _quitflag(false), m_type(type) { pthread_mutex_init(&m_lock, NULL); };
	/** 소멸자 */
    virtual ~CSocketWorkerThread() { pthread_mutex_destroy(&m_lock); };
	/** 쓰레드 기동 메쏘드 */
    virtual void run();
	/**	EVENT REPOPRT METHOD */
	void processEventMessage();
	/** ACCEPT COMMAND FROM SMS MANAGER */
	void processCommandMessage();
	/** REPORT AGENT SESSION STATUS */
	void processSessionStatus();
	/** 쓰레드 잠금 메쏘드 */
	void lock();
	/** 쓰레드 잠금 해지 메쏘드 */
	void unlock();
	/** 쓰레드 종료 요청 메쏘드 */
    void quit();
	/**
	 *	SMS Manager가 SMS Agent로 접속하기 위해 필요한 로그인 인증 절차를 처리하는 메쏘드.
	 *	@return true if login success, else return false.
	 */
	bool login();

private:
	bool *m_session_status;	/**< socket session status */
	int m_port;	/**< socket listen port */
	int m_type;	/**< 메시지 처리 타입(EVENT REPORT, ACCEPT COMMAND, SESSION STATUS REPORT) */
	void *m_data;	/**< data */
	CAgentEnvVar *m_envvar;	/**< SMS Agent 환경 정보를 관리하는 클래스 */

    int _numElts;	/**< 의미없음. */
    volatile bool _quitflag;	/**< 쓰레드 종료여부 플래그 */
	pthread_mutex_t m_lock;		/**< 쓰레드 잠금 키 */
    //OpenThreads::Mutex _quitmutex;
};

void startSocketWorkerThread(CAgentEnvVar *envvar, void *data, bool *b, int port, int type);


#endif /* __CSOCKETWORKERTHREADH__ */
