

#ifndef __CDBPOOL_H__
#define __CDBPOOL_H__

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <pthread.h>

#include "CQueue.h"
#include "CDBSession.h"

#define USERID   "system"
#define PASSWORD "manager"


//! Database pool class.
/**
 *	수집 쓰레드에서 데이터 베이스 접근에 필요한 데이터베이스 connect session을 관리하는 클래스.
 */
class CDBPool
{
	public:
		/** 생성자 */
		CDBPool();
		/** 소멸자 */
		virtual ~CDBPool();
		/**
		 *	새로운 데이터베이스 연결 세션을 추가하는 메쏘드.
		 *	@param CDBSession pointer.
		 *	@see CDBSession
		 */
		void putSession(CDBSession *session);
		/**
		 *	주어진 User ID, password, SID에 해당하는 Database session을 얻어오는 메쏘드.
		 *	@param oracle user id.
		 *	@param password.
		 *	@param Oracle SID.
		 *	@return CDBSession pointer.
		 *	@see CDBSession
		 */
		CDBSession *getSession(char *userid, char *passwd, char *sid);
		/**
		 *	주어진 key에 해당하는 Database session을 얻어오는 메쏘드.
		 *	@param database session key(character string).
		 *	@return CDBSession pointer.
		 *	@see CDBsession
		 */
		CDBSession *getSession(char *key);
		/**
		 *	얻어온 Database session을 Database pool로 반납하는 메쏘드.
		 *	@param CDBSession pointer.
		 *	@see CDBSession
		 */
		void returnSession(CDBSession *);
		/**
		 *	현재 데이터베이스 pool에 저장된 Database 연결 세션 개수을 얻어온는 메쏘드.
		 *	@return database session count.
		 */
		int size();

	private:
		pthread_mutex_t m_mutex;	/**< db pool lock key */
		CQueue *m_pool;				/**< db pool queue */
};

#endif
