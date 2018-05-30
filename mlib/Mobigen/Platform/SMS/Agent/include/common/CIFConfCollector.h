


#ifndef __CIFCONFCOLLECTOR_H__
#define __CIFCONFCOLLECTOR_H__ 1

#include "CCollector.h"


//! Interface 구성 정보를 수집하는 클래스.
/**
 *	Interface device name, speed, Mac Address, IP address 정보를 수집하는 클래스.
 */
class CIFConfCollector:public CCollector
{
	public:
		/**
		 * 생성자.
		 */
		CIFConfCollector();

		/**
		 * 소멸자.
		 */
		~CIFConfCollector();

		/**
		 * Interface 구성 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();

		/**
		 *	수집된 Interface 구성 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();

		/**
		 *	장애 판단을 위한 메쏘드. 현재 사용되지 않음.
		 */
		void isOverThreshold(CItemCondition *cond){};

	private:
		scCoreView *m_coreview;			/**< system kernel 정보를 조회하기 위한 core 구조체 */
		scInterfaceStatus *m_ifstat;	/**< Interface 상태 정보를 조회하기 위한 구조체 */
		v_list_t *m_list;				/**< scInterfaceStatus 구조체를 저장하고 있는 리스트 */
};

#endif /* __CIFCONFCOLLECTOR_H__ */
