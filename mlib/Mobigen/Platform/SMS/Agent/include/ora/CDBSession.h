
#ifndef __CDBSESSION_H__
#define __CDBSESSION_H__

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <errno.h>
#include <pthread.h>

#include "CQueue.h"

//! Database 연결 세션 정보를 관리하는 클래스(Thread safe).
class CDBSession
{
	public:
		/** 생성자 */
		CDBSession();
		/** 소멸자 */
		virtual ~CDBSession();
		/**
		 *	오라클 데이터베이스로 접속을 시도하는 메쏘드.
		 *	@return return 1 if success, else return -1
		 */
		int connect();
		/**
		 *	오라클 데이터베이스로 접속을 시도하는 메쏘드.
		 *	@param 계정 정보(userid/passwd@sid)
		 *	@return return 1 if success, else return -1
		 */
		int connect(char *account);
		/**
		 *	오라클 데이터베이스로 접속을 시도하는 메쏘드.
		 *	@param userid
		 *	@param password
		 *	@param oracle sid
		 *	@return return 1 if success, else return -1
		 */
		int connect(char *userid, char *password, char *sid);
		/**
		 *	오라클 접속에 필요한 계정 정보를 설정하는 메쏘드.
		 *	@param oracle sid.
		 *	@param userid.
		 *	@param password.
		 */
		void setOraInfo(const char * sid, const char * userid, const char * password);
		/**
		 *	Oracle connection을 얻어오는 메쏘드. 오라클 세션 동기화 메쏘드.
		 *	@return sql_context pointer.
		 */
		void * getConnection();
		/**
		 *	Oracle connection을 close하는 메쏘드.
		 */
		void closeConnection();
		/**
		 *	Oracle session을 반납하는 메쏘드. 오라클 세션 동기화 메쏘드.
		 */
		void returnConnection();
		/**
		 *	오라클 세션 키를 등록하는 메쏘드. 세션 키는 "userid/password@sid"로 이루어진다.
		 *	@param userid
		 *	@param password
		 *	@param sid
		 */
		void setKey(char *userid, char *password, char *sid);
		/**
		 *	오라클 세션 키를 등록하는 메쏘드. 세션 키는 "userid/password@sid"로 이루어진다.
		 *	@param userid/password@sid
		 */
		void setKey(char *account);
		/**
		 *	오라클 세션 키를 얻어오는 메쏘드.
		 *	@return Oracle session key(userid/password@sid)
		 */
		char *getKey();
		/**
		 *	Oracle database session이 연결되어 있는지 확인하는 메쏘드.
		 *	@return return true if database is open, else return false.
		 */
		bool isOpen();

	private:
		pthread_mutex_t m_mutex;	/**< db session lock key */
		char orasid[32];			/**< oracle sid */
		char oradba[32];			/**< oracle user id */
		char orapw[32];				/**< oracle password */
		char m_key[128];			/**< userid/password@sid */
		int m_count;				/**< 의미 없음. */
		CQueue *m_dbq;				/**< 의미 없음. */
		void *m_session;			/**< database session (sql_context) */
		int m_idx[10];				/**< 의미 없음. */
		bool m_status;				/**< database session status */
};

#endif
