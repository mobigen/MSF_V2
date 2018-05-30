


#ifndef __CDISKCONFCOLLECTOR_H__
#define __CDISKCONFCOLLECTOR_H__ 1

#include "CCollector.h"


//! Disk 구성 정보를 수집하는 클래스.
/**
 *	Disk device, mount point, total size(MB) 정보를 수집하는 클래스.
 */
class CDiskConfCollector:public CCollector
{
	public:
		/** 생성자 */
		CDiskConfCollector();
		/** 소멸자 */
		~CDiskConfCollector();

		/**
		 * Disk 구성 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();

		/**
		 *	수집된 Disk 구성 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();

		/**
		 *	장애 판단을 위한 메쏘드. 현재 사용되지 않음.
		 */
		void isOverThreshold(CItemCondition *cond){};

	private:
		scCoreView *m_coreview;	/**< system kernel 정보를 조회하기 위한 kernel core 변수 */
		scFSInfo *m_fsinfo;		/**< file system 정보를 조회하기 위한 변수 */
		v_list_t *m_list;		/**< scFSInfo 구조체를 시스템 mount point 개수만큼 저장하고 있는 리스트 */
};

#endif /* __CDISKCONFCOLLECTOR_H__ */
