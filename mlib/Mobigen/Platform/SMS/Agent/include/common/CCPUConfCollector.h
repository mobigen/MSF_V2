


#ifndef __CCPUCONFCOLLECTOR_H__
#define __CCPUCONFCOLLECTOR_H__ 1

#include "CCollector.h"

//! CPU 구성 정보를 수집하는 클래스.
/**
 *	cpu index("cpu0", "cpu1", ...) 및 CPU Clock Hz 정보를 수집하는 클래스.
 *	CPU Naming Rule : cpu0, cpu1, cpu2, ...., total
 */
class CCPUConfCollector:public CCollector
{
	public:
		/**
		 * 생성자.
		 */
		CCPUConfCollector();
		/**
		 * 소멸자.
		 */
		~CCPUConfCollector();

		/**
		 * CPU 구성 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();

		/**
		 *	수집된 CPU 구성 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();

		/**
		 *	장애 판단을 위한 메쏘드. 현재 사용되지 않음.
		 */
		void isOverThreshold(CItemCondition *cond){};

	private:
		scCoreView *m_coreview;		/**< system kernel 정보를 조회하기 위한 kernel core 변수 */
		scSysInfo m_sysinfo;		/**< system 기본 정보를 조회하기 위한 변수. cpu 개수 및 Hz정보 포함 */
		scCpuStatus m_ucpu, m_mcpu[SC_MAX_CPU_NUM];	/**< total cpu, 개별 cpu 정보를 조회하기 위한 변수 */
		int m_ncpu;					/**< cpu 개수 */
};

#endif /* __CCPUCONFCOLLECTOR_H__ */
