
#ifndef __CSCHEDULERTHREADH__
#define __CSCHEDULERTHREADH__

#include "CPolicyItem.h"
#include "SCThreadObserver.h"

//! item의 정책을 수행하는 스케쥴러 쓰레드 클래스
/**
 *	item의 정보 수집 주기 및 장애 정보 수집 주기를 검사하여, 수집 주기가 된 item에 대해서
 *	정보 수집 쓰레드에게 정보 수집을 요청하고, 해당 아이템에 다음 정책을 설장하는 클래스.
 */
class CSchedulerThread : public OpenThreads::Thread, public ThreadReporter {

public:
	/**
	 *	생성자
	 *	@param 데이터 포인터.
	 *	@param element number 의미 없음.
	 */
    CSchedulerThread(void *_data, int numElts) : OpenThreads::Thread(), 
	ThreadReporter(),
        m_data(_data), _numElts(numElts), _quitflag(false) { pthread_mutex_init(&m_lock, NULL); };
	/** 소멸자 */
    virtual ~CSchedulerThread() { pthread_mutex_destroy(&m_lock); };
	/**
	 *	쓰레드 기동 메쏘드. 실 비지니스 로직이 존재하는 메쏘드이다.
	 */
    virtual void run();
	/** thread 잠금 메쏘드 */
	void lock();
	/**	thread 잠금 해지 메쏘드. */
	void unlock();
	/** 
	 *	CItem에 존재하는 인스턴스 정보를 instance name queue를 생성하여
	 *	item 정책 클래스(CPolicyItem)에 설정하는 메쏘드
	 *	@param instance name queue를 설정할 CPolicyItem pointer.
	 *	@param 인스턴스 정보가 존재하는 CItem pointer.
	 */
	void addInstanceToPollItem(CPolicyItem *pollitem, CItem *item);
	/**
	 *	thread 종료 요청 메쏘드.
	 */
    void quit();

private:
	void *m_data;	/**< 쓰레드 기동에 필요한 데이터 */

    int _numElts;	/**< 의미없음. */
    volatile bool _quitflag;	/**< 쓰레드 종료 플래그 */
	pthread_mutex_t m_lock;	/**< 쓰레드 잠금 키 */
};

void startSchedulerThread(void *data);


#endif /* __CSCHEDULERTHREADH__ */
