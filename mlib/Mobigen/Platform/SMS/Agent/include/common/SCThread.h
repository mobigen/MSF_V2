
#ifndef __SCTHREADH__
#define __SCTHREADH__

#include "CPolicyItem.h"

#include "CCollectorHeader.h"

#include "SCThreadObserver.h"

//! 스케쥴러에 의해 요청된 item에 대해 정보 수집을 수행하는 쓰레드.
class SCThread : public OpenThreads::Thread, public ThreadReporter {

public:
	/**
	 *	생성자
	 *	@param	data pointer.
	 *	@param 의미없음.
	 */
    SCThread(void *_data, int numElts) : OpenThreads::Thread(), 
	ThreadReporter(),
        m_data(_data), _numElts(numElts), _quitflag(false) { pthread_mutex_init(&m_lock, NULL); };
	/** 소멸자 */
    virtual ~SCThread() { pthread_mutex_destroy(&m_lock); };
	/** 쓰레드 기동 요청 메쏘드 */
    virtual void run();
	/** 쓰레드 잠금 메쏘드 */
	void lock();
	/** 쓰레드 잠금 해지 메쏘드 */
	void unlock();
	/** 쓰레드 종료 요청 메쏘드 */
    void quit();
	/**
	 *	정보 수집기(CCollector)의 기동을 요청하는 메쏘드.
	 *	@param 수집 대상 정책 item 정보.
	 *	@see CCollector, CPolicyItem
	 */
    void invokeCollector(CPolicyItem *pitem);

private:
	void *m_data;	/**< data poiner */

    int _numElts;	/**< 의미없음 */
    volatile bool _quitflag;	/**< 쓰레드 종료 요청 플래그 */
	pthread_mutex_t m_lock;		/**< 쓰레드 잠금 키 */
    //OpenThreads::Mutex _quitmutex;
};

void startThreadWorker(void *data, int thread_num);


#endif /* __SCTHREADH__ */
