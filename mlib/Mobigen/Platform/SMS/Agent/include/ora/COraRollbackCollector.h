


#ifndef __CORAROLLBACKCOLLECTOR_H__
#define __CORAROLLBACKCOLLECTOR_H__ 1

#include "CCollector.h"

/**
 * Oracle Rollback status 정보를 저장하는 구조체
 */
typedef struct _st_rollback {
	char 		name[32];
	char 		status[20];
	int			extends;
	int			shrinks;
	int			wraps;
	int			aveshrink;
	long		aveactive;
	long		waits;
	long		gets;
	unsigned long long		writes;
	int			active_trans;
}st_rollback;

//! Rollback 상태 정보(Rollback segment name, status)를 수집하는 클래스
class COraRollbackCollector:public CCollector
{
	public:
		/** 생성자 */
		COraRollbackCollector();
		/** 소멸자 */
		virtual ~COraRollbackCollector();
		/**
		 * Oracle rollback segment status 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();
		/**
		 *	Oracle에 SQL Query를 질의하여 결과를 얻어오는 메쏘드.
		 */
		bool collectOraData();
		/**
		 *	수집된 Oracle rollback segment status 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();

		/**
		 *	장애 판단을 위한 메쏘드. 현재 사용되지 않음.
		 */
		void isOverThreshold(CItemCondition *cond);

		/**
		 *	OraRollback 성능 임계치 장애를 발생시키는 메쏘드.
		 *	임계치를 초과한 경우에는 장애를 발생시키고, 
		 *	이전에 장애가 발생한 적이 있고, 임계치를 초과하지 않은 경우에는 장애를 해지시킨다.
		 *
		 *	@param CItemCondition pointer.
		 *	@param character item name.
		 *	@param 성능 임계치 초과 여부. 임계치를 넘은 경우는 true, 초과하지 않은 경우 false.
		 *	@param st_rollback 성능 정보를 저장하고 있는 구조체.
		 */
		void checkAlarm(CItemCondition *cond, char *instname, bool b, st_rollback *status);

	private:
		v_list_t *m_list;			/**< rollback segment 정보를 저장하는 리스트 */
		st_rollback *m_rollback;	/**< rollback segment 정보를 조회하기 위한 구조체 */
};

#endif /* __CORAROLLBACKCOLLECTOR_H__ */
