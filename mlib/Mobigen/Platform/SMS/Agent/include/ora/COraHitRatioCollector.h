


#ifndef __CORAHITRATIOCOLLECTOR_H__
#define __CORAHITRATIOCOLLECTOR_H__ 1

#include "CCollector.h"

//! Oracle buffer cache hit ratio, library cache hit ratio, data dictionary hit ratio 정보를 수집하는 클래스.
class COraHitRatioCollector:public CCollector
{
	public:
		/** 생성자 */
		COraHitRatioCollector();
		/** 소멸자 */
		virtual ~COraHitRatioCollector();
		/**
		 * Oracle  buffer cache hit ratio, library cache hit ratio, data dictionary hit ratio 정보를 수집하여 SMS Manager로 전송하기 위한 메시지 포맷으로
		 * 변환하여 메시지 큐로 전송하는 메쏘드.
		 */
		void collect();
		/**
		 *	Oracle에 SQL Query를 질의하여 결과를 얻어오는 메쏘드.
		 */
		bool collectOraData();
		/**
		 *	수집된 buffer cache hit ratio, library cache hit ratio, data dictionary hit ratio 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 */
		void makeMessage();

		/**
		 *	장애 판단을 위한 메쏘드. 현재 사용되지 않음.
		 */
		void isOverThreshold(CItemCondition *cond);

		/**
		 *	OraHitRatio 성능 임계치 장애를 발생시키는 메쏘드.
		 *	임계치를 초과한 경우에는 장애를 발생시키고, 
		 *	이전에 장애가 발생한 적이 있고, 임계치를 초과하지 않은 경우에는 장애를 해지시킨다.
		 *
		 *	@param CItemCondition pointer.
		 *	@param character Item name.
		 *	@param 성능 임계치 초과 여부. 임계치를 넘은 경우는 true, 초과하지 않은 경우 false.
		 */
		void checkAlarm(CItemCondition *cond, char *instname, bool b);

	private:
		double m_buf; /**< buffer cache */
		double m_lib; /**< library cache */
		double m_dic; /**< dictionary cache */
};

#endif /* __CORAHITRATIOCOLLECTOR_H__ */
