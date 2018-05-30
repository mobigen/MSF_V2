


#ifndef __CIFPERFCOLLECTOR_H__
#define __CIFPERFCOLLECTOR_H__ 1

#include "CCollector.h"


//! Interface 성능 정보를 수집하는 클래스.
/**
 *	Interface packet in, packet out, packet in error, packet out error, collisions 정보를 수집하는 클래스.
 */
class CIFPerfCollector:public CCollector
{
	public:
		/**
		 * 생성자.
		 */
		CIFPerfCollector();
		/** 소멸자 */
		~CIFPerfCollector();

		/**
		 * Interface 성능 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();

		/**
		 *	수집된 Interface 성능 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();

		/**
		 *	수집된 Interface 성능 정보를 CItemCondition에 주어진 임계치 정보와 비교하여
		 *	장애 판단을 하여 장애를 발생시키는 메쏘드.
		 *	@param CItemCondition pointer.
		 *	@see CItemCondition
		 */
		void isOverThreshold(CItemCondition *cond);

		/**
		 *	Interface 성능 임계치 장애를 발생시키는 메쏘드.
		 *	임계치를 초과한 경우에는 장애를 발생시키고, 
		 *	이전에 장애가 발생한 적이 있고, 임계치를 초과하지 않은 경우에는 장애를 해지시킨다.
		 *
		 *	@param CItemCondition pointer.
		 *	@param character interface name.
		 *	@param 성능 임계치 초과 여부. 임계치를 넘은 경우는 true, 초과하지 않은 경우 false.
		 *	@param Interface 성능 정보를 저장하고 있는 구조체.
		 */
		void checkAlarm(CItemCondition *cond, char *instname, bool b, scInterfaceStatus *status);

	private:
		scCoreView *m_coreview;			/**< system kernel 정보를 조회하기 위한 core 구조체 */
		scInterfaceStatus *m_ifstat;	/**< Interface 상태 정보를 조회하기 위한 구조체 */
		v_list_t *m_list;				/**< scInterfaceStatus 구조체를 저장하고 있는 리스트 */
};

#endif /* __CIFPERFCOLLECTOR_H__ */
