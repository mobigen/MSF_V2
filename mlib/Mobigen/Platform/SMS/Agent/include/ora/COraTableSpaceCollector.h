


#ifndef __CORATABLESPACECOLLECTOR_H__
#define __CORATABLESPACECOLLECTOR_H__ 1

#include "CCollector.h"

/** oracle tablespace 정보를 저장하는 구조체 */
typedef struct _st_tspace {
	char name[32];
	char status[12];
	long total;
	long _free;
	long largest;
	double usage;
}st_tspace;

//! Oracle tablespace 정보를 수집하는 클래스.
/**
 *	tablespace의 name, status, total size, free size, usage 등의 정보를 수집하는 클래스.
 */
class COraTableSpaceCollector:public CCollector
{
	public:
		/** 생성자 */
		COraTableSpaceCollector();
		/** 소멸자 */
		virtual ~COraTableSpaceCollector();
		/**
		 * Oracle tablespace 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();
		/**
		 *	Oracle에 SQL Query를 질의하여 결과를 얻어오는 메쏘드.
		 */
		bool collectOraData();
		/**
		 *	수집된 Oracle tablespace 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();

		/**
		 *	장애 판단을 위한 메쏘드. 현재 사용되지 않음.
		 */
		void isOverThreshold(CItemCondition *cond);

		/**
		 *	OraTableSpace 성능 임계치 장애를 발생시키는 메쏘드.
		 *	임계치를 초과한 경우에는 장애를 발생시키고, 
		 *	이전에 장애가 발생한 적이 있고, 임계치를 초과하지 않은 경우에는 장애를 해지시킨다.
		 *
		 *	@param CItemCondition pointer.
		 *	@param character item name.
		 *	@param 성능 임계치 초과 여부. 임계치를 넘은 경우는 true, 초과하지 않은 경우 false.
		 *	@param OraTableSpace 성능 정보를 저장하고 있는 구조체.
		 */
		void checkAlarm(CItemCondition *cond, char *instname, bool b, st_tspace *status);

	private:
		v_list_t *m_list;		/**< tablespace 정보를 저장할 리스트 */
		st_tspace *m_tspace;	/**< tablespace 정보를 조회하기 위한 구조체 */
};

#endif /* __CORATABLESPACECOLLECTOR_H__ */
