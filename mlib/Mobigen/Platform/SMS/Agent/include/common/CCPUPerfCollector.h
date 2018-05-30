


#ifndef __CCPUPERFCOLLECTOR_H__
#define __CCPUPERFCOLLECTOR_H__ 1

#include "CCollector.h"

extern scCpuStatus g_ucpu, g_mcpu[SC_MAX_CPU_NUM];
extern int g_ncpu;
extern time_t g_cputime;


//! CPU 성능 정보를 수집하는 클래스.
/**
 *	개별 cpu 및 Total CPU의 system, user, cpu, wait, idle 정보를 수집하는 클래스.
 *	CPU Naming Rule : cpu0, cpu1, cpu2, ...., total
 */
class CCPUPerfCollector:public CCollector
{
	public:
		/** 생성자 */
		CCPUPerfCollector();
		/** 소멸자 */
		~CCPUPerfCollector();

		/**
		 * CPU 성능 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();

		/**
		 *	수집된 CPU 성능 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();

		/**
		 *	수집된 CPU 성능 정보를 CItemCondition에 주어진 임계치 정보와 비교하여
		 *	장애 판단을 하여 장애를 발생시키는 메쏘드.
		 *	@param CItemCondition pointer.
		 *	@see CItemCondition
		 */
		void isOverThreshold(CItemCondition *cond);

		/**
		 *	CPU 성능 임계치 장애를 발생시키는 메쏘드.
		 *	임계치를 초과한 경우에는 장애를 발생시키고, 
		 *	이전에 장애가 발생한 적이 있고, 임계치를 초과하지 않은 경우에는 장애를 해지시킨다.
		 *
		 *	@param CItemCondition pointer.
		 *	@param character CPU name.
		 *	@param 성능 임계치 초과 여부. 임계치를 넘은 경우는 true, 초과하지 않은 경우 false.
		 *	@param CPU 성능 정보를 저장하고 있는 구조체.
		 */
		void checkAlarm(CItemCondition *cond, char *instname, bool b, scCpuStatus *status);

	private:
		scCoreView *m_coreview;		/**< system kernel 정보를 조회하기 위한 kernel core 변수 */
		scCpuStatus m_ucpu, m_mcpu[SC_MAX_CPU_NUM]; /**< total cpu 및 개별 cpu의 성능 정보를 조회하기 위한 변수 */
		int m_ncpu;					/**< Total CPU 개수 */
};

#endif /* __CCPUPERFCOLLECTOR_H__ */
