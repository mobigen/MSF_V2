


#ifndef __CORATOPSQLCOLLECTOR_H__
#define __CORATOPSQLCOLLECTOR_H__ 1

#include "CCollector.h"

/** 최근에 오라클에서 수행된 SQL 정보를 저장하기 위한 구조체 */
typedef struct _st_topsql {
	char _sqltext[1024];
	int executions;
	int buffergets;
	int diskreads;
	int rowsprocessed;
}st_topsql;

//! EXECUTIONS, BUFFER_GETS, DISK_READS, ROWS_PROCESSED 등의 최근에 수행된 SQL문 정보를 수집하는 클래스.
class COraTopSqlCollector:public CCollector
{
	public:
		/** 생성자 */
		COraTopSqlCollector();
		/** 소멸자 */
		virtual ~COraTopSqlCollector();
		/**
		 *  EXECUTIONS, BUFFER_GETS, DISK_READS, ROWS_PROCESSED 등의 최근에 수행된 SQL문 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();
		/**
		 *	Oracle에 SQL Query를 질의하여 결과를 얻어오는 메쏘드.
		 */
		bool collectOraData();
		/**
		 *	EXECUTIONS, BUFFER_GETS, DISK_READS, ROWS_PROCESSED 등의 최근에 수행된 SQL문 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();

		/**
		 *	장애 판단을 위한 메쏘드. 현재 사용되지 않음.
		 */
		void isOverThreshold(CItemCondition *cond);

		/**
		 *	OraTopSql 성능 임계치 장애를 발생시키는 메쏘드.
		 *	임계치를 초과한 경우에는 장애를 발생시키고, 
		 *	이전에 장애가 발생한 적이 있고, 임계치를 초과하지 않은 경우에는 장애를 해지시킨다.
		 *
		 *	@param CItemCondition pointer.
		 *	@param character CPU name.
		 *	@param 성능 임계치 초과 여부. 임계치를 넘은 경우는 true, 초과하지 않은 경우 false.
		 *	@param Process 성능 정보를 저장하고 있는 구조체.
		 */
		void checkAlarm(CItemCondition *cond, char *instname, bool b, st_topsql *status);

	private:
		v_list_t *m_list;		/**< 수행된 SQL 정보를 저장하기 위한 리스트 */
		st_topsql *m_topsql;	/**< SQL 정보를 조회하기 위한 구조체 */
		int m_topn;				/**< 조회할 상위 TOP N */
		int m_sort;				/**< 정렬 순서. 1 : EXECUTIONS, 2 : BUFFER_GETS, 3 : DISK_READS, 4 : ROWS_PROCESSED, else DISK_READS */
};

#endif /* __CORATOPSQLCOLLECTOR_H__ */
