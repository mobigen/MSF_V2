
#ifndef __CSYSLOGMONITORTHREADH__
#define __CSYSLOGMONITORTHREADH__

#include "CAgentEnvVar.h"
#include "CMessageFormatter.h"
#include "SCThreadObserver.h"

//! 시스로그를 모니터링하는 클래스
class CSyslogMonitorThread : public OpenThreads::Thread, public ThreadReporter {

public:
	/**
	 *	생성자
	 *	@param 쓰레드 기동에 필요한 data pointer.
	 */
    CSyslogMonitorThread(void *_data, int numElts) : OpenThreads::Thread(), 
	ThreadReporter(),
        m_data(_data), _numElts(numElts), _quitflag(false) { pthread_mutex_init(&m_lock, NULL); };
	/** 소멸자 */
    virtual ~CSyslogMonitorThread() { pthread_mutex_destroy(&m_lock); };
	/** 쓰레드 기동 메쏘드 */
    virtual void run();
	/** syslog file pointer의 현재 위치 정보를 판단하는 메쏘드 */
	void checkFD();
	/**	
	 *	수집된 syslog 메시지가 주어진 item condition의 조건에 만족하는지 여부를 확인하는 메쏘드.
	 *	@param	syslog message
	 */
	void checkCondition(char *log);
	/**
	 *	수집된 syslog 메시지를 SMS Manager로 전송하기 위해 데이터 버퍼로 전송하는 메쏘드.
	 *	@param CItemCondition pointer.
	 *	@param syslog message.
	 *	@see CItemCondition.
	 */
	void sendEvent(CItemCondition *cond, char *log);
	/** 쓰레드 잠금 메쏘드 */
	void lock();
	/** 쓰레드 잠금 해지 메쏘드 */
	void unlock();
	/** 쓰레드 종료 요청 메쏘드 */
    void quit();

private:
	FILE *m_fd;				/**< Syslog file pointer */
	void *m_data;			/**< data */
	CAgentEnvVar *m_envvar;	/**< SMS Agent 환경 정보를 관리하는 클래스 */ 
	CItem *m_item;			/**< syslog item 정보 클래스 */
    int _numElts;			/**< 의미 없음. */
	unsigned long m_offset;	/**< syslog file 데이터를 읽은 최종 위치 정보 */
    volatile bool _quitflag;	/**< 쓰레드 종료 요청 플래그 */
	pthread_mutex_t m_lock;	/**< 쓰레드 잠금 키 */
	std::string m_filename;	/**< syslog 파일명 */
    //OpenThreads::Mutex _quitmutex;
};

void startSyslogThread(void *data, int thread_num);


#endif /* __CSYSLOGMONITORTHREADH__ */
