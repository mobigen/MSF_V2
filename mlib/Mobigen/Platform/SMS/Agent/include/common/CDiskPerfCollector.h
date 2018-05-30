


#ifndef __CDISKPERFCOLLECTOR_H__
#define __CDISKPERFCOLLECTOR_H__ 1

#include "CCollector.h"


//! Disk 성능 정보를 수집하는 클래스.
/**
 *	File System(Device name, Mount Point, Total size(MB), Used(MB), Free(MB), Usage(%)) 정보를 수집하는 클래스.
 */
class CDiskPerfCollector:public CCollector
{
	public:
		/** 생성자 */
		CDiskPerfCollector();
		/** 소멸자 */
		~CDiskPerfCollector();

		/**
		 * Disk 성능 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();

		/**
		 *	수집된 Disk 성능 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();

		/**
		 *	장애 판단을 위한 메쏘드. 현재 사용되지 않음.
		 */
		void isOverThreshold(CItemCondition *cond);

		/**
		 *	Disk 성능 임계치 장애를 발생시키는 메쏘드.
		 *	임계치를 초과한 경우에는 장애를 발생시키고, 
		 *	이전에 장애가 발생한 적이 있고, 임계치를 초과하지 않은 경우에는 장애를 해지시킨다.
		 *
		 *	@param CItemCondition pointer.
		 *	@param character CPU name.
		 *	@param 성능 임계치 초과 여부. 임계치를 넘은 경우는 true, 초과하지 않은 경우 false.
		 *	@param Disk 성능 정보를 저장하고 있는 구조체.
		 */
		void checkAlarm(CItemCondition *cond, char *instname, bool b, scFSInfo *status);

	private:
		scCoreView *m_coreview;		/**< system kernel 정보를 조회하기 위한 kernel core 변수 */
		scFSInfo *m_fsinfo;			/**< file system 정보를 조회하기 위한 변수 */
		v_list_t *m_list;			/**< scFSInfo 구조체를 시스템 mount point 개수만큼 저장하고 있는 리스트 */
};

#endif /* __CDISKPERFCOLLECTOR_H__ */
