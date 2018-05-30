


#ifndef __CNETWORKSESSIONCOLLECTOR_H__
#define __CNETWORKSESSIONCOLLECTOR_H__ 1

#include "CCollector.h"


//!  네트워크 세션 정보를 수집하는 클래스.
/**
 *	Local IP, Local Port, Remote IP, Remote Port 정보를 조회하는 클래스.
 */
class CNetworkSessionCollector:public CCollector
{
	public:
		/** 생성자 */
		CNetworkSessionCollector();
		/** 소멸자 */
		~CNetworkSessionCollector();
		/**
		 *	네트워크 세션 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();
		/**
		 *	수집된 네트워크 세션 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();
		/**
		 *	장애 판단을 위한 메쏘드. 현재 사용되지 않음.
		 */
		void isOverThreshold(CItemCondition *cond){};

	private:
		scCoreView *m_coreview;	/**< system kernel 정보를 조회하기 위한 kernel core 변수 */
		scTCPInfo *m_tcpinfo;		/**< 개별 네드워크 세션  정보를 조회하기 위한 변수 */
		v_list_t *m_list;		/**< TCP 네트워크 세션  정보를 저장하는 리스트 */
};

#endif /* __CNETWORKSESSIONCOLLECTOR_H__ */
