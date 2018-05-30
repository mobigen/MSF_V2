


#ifndef __CTOPCPUPROCESSPERFCOLLECTOR_H__
#define __CTOPCPUPROCESSPERFCOLLECTOR_H__ 1

#include "CCollector.h"

//! CPU 점유율 순서로 Top N개의 프로세스 정보를 수집하는 클래스.
/**
 *	scagent.xml 파일에 다음과 같이 설정되어 있다면,\n
 *	<instances>\n
 *		<instance name="cpu|5">cpu|5</instance>\n
 *  </instances>\n
 *	CPU 점유율 상위 5개의 프로세스 정보를 수집하여 처리한다.
 */
class CTopCPUProcessPerfCollector:public CCollector
{
	public:
		/** 생성자 */
		CTopCPUProcessPerfCollector();
		/** 소멸자 */
		~CTopCPUProcessPerfCollector();
		/**
		 * CPU 점유율 순서로 Top N개의 프로세스 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();
		/**
		 *	수집된 CPU 점유율 순서로 Top N개의 프로세스 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();
		/**
		 *	장애 판단을 위한 메쏘드. 현재 사용되지 않음.
		 */
		void isOverThreshold(CItemCondition *cond){};

	private:
		scCoreView *m_coreview;	/**< system kernel 정보를 조회하기 위한 kernel core 변수 */
		scPSInfo *m_psinfo;		/**< 프로세스 상세 정보를 조회하기 위한 변수 */
		v_list_t *m_list;		/**< 프로세스 상세 정보를 저장하기 위한 리스트 */
};

#endif /* __CTOPCPUPROCESSPERFCOLLECTOR_H__ */
