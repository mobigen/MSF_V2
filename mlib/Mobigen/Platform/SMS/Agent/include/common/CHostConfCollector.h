


#ifndef __CHOSTCONFCOLLECTOR_H__
#define __CHOSTCONFCOLLECTOR_H__ 1

#include "CCollector.h"

//! 호스트의 기본 구성 정보를 수집하는 클래스.
/**
 *	HostName, IP Address, OSType, OSVersion, Model, Hostid 정보를 수집하는 클래스.
 */
class CHostConfCollector:public CCollector
{
	public:
		/**
		 * 생성자.
		 */
		CHostConfCollector();
		/**
		 * 소멸자.
		 */
		~CHostConfCollector();

		/**
		 * 호스트의 기본 구성 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();

		/**
		 *	수집된 기본 구성 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();

		/**
		 *	장애 판단을 위한 메쏘드. 현재 사용되지 않음.
		 */
		void isOverThreshold(CItemCondition *cond){};

	private:
		scCoreView *m_coreview;	/**< system kernel 정보를 조회하기 위한 core 구조체 */
		scSysInfo m_sysinfo;	/**< system 기본 정보를 저장하기 위한 구조체 */
		char m_ipaddr[64];		/**< host ip address */
		long m_hostid;			/**< hostid */
};

#endif /* __CHOSTCONFCOLLECTOR_H__ */
