
#ifndef _CITEM_H__
#define _CITEM_H__ 1


#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <time.h>
#include <string>
#include <iostream>

#include "CQueue.h"
#include "CItemInstance.h"
#include "CItemCondition.h"

typedef struct _st_item_alarm {
	char instance[128];
	int condid;
} st_item_alarm;

//! 수집 대상 item 정보 객체.
/**
 *	item code, 수집 주기(schedule), 장애 수집 주기(eschedule), 수집여부(enable), 상세수집여부(method)
 *	수집 대상 instance, 장애 임계치 판단 condition 정보 등을 관리한다.
 */

class CItem
{
	public:
		/** 생성자 */
		CItem();
		/** 소멸자 */
		virtual ~CItem();
		/**
		 *	method for getting item code.
		 *	@return item code.
		 */
		std::string getCode() { return m_code; }
		/**
		 *	method for getting item description.
		 *	@return item code description.
		 */
		std::string getName() { return m_name; }

		/**
		 *	method for getting schedule(정보 수집 주기) period.
		 *	@return schedule period.
		 */
		unsigned long getSchedule() { return m_schedule; }

		/**
		 *	method for getting event schedule period(장애 수집 주기).
		 *	@return event schedule period.
		 */
		unsigned long getEventSchedule() { return m_eventSchedule; }
		/**
		 *	정보 수집 여부를 반환하는 메쏘드.
		 *	@return 정보 수집 여부('O', 'X')
		 */
		std::string getEnable() { return m_enable; }
		/**
		 *	유형별 정보 수집 여부를 반환하는 메쏘드(ACTIVE/PASSIVE/EVENT).
		 *	@return 정보 수집 여부('OOO', 'XXX', ...)
		 */
		std::string getMethod() { return m_method; }
		/**
		 *	정보 수집 시간을 반환하는 메쏘드.
		 *	@return 정보 수집 시간.
		 */
		time_t getCollectTime() { return m_collect; }
		/**
		 *	장애 수집 시간을 반환하는 메쏘드.
		 *	@return 정보 수집 시간.
		 */
		time_t getEventCollectTime() { return m_eventCollect; }
		/**
		 *	item별로 수집 등록된 instance(CItemInstance) 객체를 저장하고 있는 리스트를 반환하는 메쏘드.
		 *	@return instance(CItemInstance) 객체를 저장하고 있는 리스트 Queue
		 */
		CQueue *getInstanceQ() { return m_instQ; }
		/**
		 *	item별로 장애 판단 임계치 및 장애 수집 대상 instance 정보를
		 *	관리하는 condition(CItemCondition) 객체를 저장하고 있는 리스트를 반환하는 메쏘드.
		 *	@return condition(CItemCondition) 객체를 저장하고 있는 리스트 Queue
		 */
		CQueue *getConditionQ() { return m_condQ; }
		/**
		 *	condition id와 instance 명을 키로하여 장애 발생 여부 정보를 저장하고 있는 리스트를 반환하는 메쏘드.
		 *	@return 장애 발생 여부 정보.
		 */
		CQueue *getAlarmInstanceQ() { return m_alarmInstanceQ; }

		/**
		 *	item code 정보를 설정하는 메쏘드.
		 *	@param item code.
		 */
		void setCode(std::string code) { m_code = code; }
		/**
		 *	item description 정보를 설정하는 메쏘드.
		 *	@param	item description.
		 */
		void setName(std::string name) { m_name = name; }
		/**
		 *	정보 수집 주기를 설정하는 메쏘드.
		 *	@param 정보 수집 주기(초:seconds)
		 */
		void setSchedule(unsigned long schedule) { m_schedule = schedule; }
		/**
		 *	장애 정보 수집 주기를 설정하는 메쏘드.
		 *	@param 장애 정보 수집 주기(초:seconds)
		 */
		void setEventSchedule(unsigned long eventSchedule) { m_eventSchedule = eventSchedule; }
		/**
		 *	정보 수집 여부를 설정하는 메쏘드('0' or 'X')
		 *	@param 정보 수집 여부('O' or 'X')
		 */
		void setEnable(std::string enable) { m_enable = enable; }
		/**
		 *	정보 수집 상세 여부를 설정하는 메쏘드.
		 *	@param 정보 수집 상세 여부(ACTIVE/PASSIVE/EVENT)
		 */
		void setMethod(std::string method) { m_method = method; }
		/**
		 *	다음 정보 수집 시간을 설정하는 메쏘드.
		 *	@param 다음 정보 수집 시간.
		 */
		void setCollectTime(time_t collect) { m_collect = collect; }
		/**
		 *	다음 장애 수집 시간을 설정하는 메쏘드.
		 *	@param 다음 장애 수집 시간.
		 */
		void setEventCollectTime(time_t eventCollect) { m_eventCollect = eventCollect; }
		/**
		 *	현재 정보를 수집하고 있는지 여부를 판단하는 메쏘드.
		 *	현재 정보를 수집하고 있는 item은 scheduler가 수집 요청을 하지 않는다.
		 *	@param 정보 수집 여부(true : 현재 정보 수집 중, false : 정보를 수집하고 있지 않음).
		 */
		void setIsCollect(bool b) { m_isCollect = b; }

		/**
		 *	item에 수집 대상 instance를 추가하는 메쏘드.
		 *	@param	수집 대상 instance(CItemInstance) pointer.
		 */
		void addInstance(CItemInstance *inst);
		/**
		 *	item에 임계치 판단 조건을 추가하는 메쏘드.
		 *	@param 임계치 판단 조건(CItemCondition) pointer.
		 */
		void addCondition(CItemCondition *cond);
		/**
		 *	item에 현재 발생된 장애 삭제.
		 *	@param condition id, instance name을 키로 하는 삭제 대상 장애 정보.
		 */
		void delAlarm(st_item_alarm *alarm);
		/**
		 *	item에 발생한 장애를 등록.
		 *	@param condition id, instance name을 키로 하는 추가 대상 장애 정보.
		 */
		void addAlarm(st_item_alarm *alarm);
		/**
		 *	condition id, instance name을 키로 하는 장애가 발생된 적이 있는지를 판단하는 메쏘드. 장애 중복 처리를 위해 존재.
		 *	@param condition id, instance name을 키로 하는 장애 정보.
		 */
		bool isAlarm(st_item_alarm *alarm);
		
		/**
		 *	현재 item에 대해 정보를 수집중인지 아닌지 여부를 판단하는 메쏘드.
		 *	@return true : 수집중, false : 수집 가능.
		 */
		bool isCollect() { return m_isCollect; }
		/**
		 *	정보 수집 가능 여부를 판단하는 메쏘드.
		 *	@return true : 수집 가능,  false : 수집 불가.
		 */
		bool isEnable();
		/**
		 *	SMS Manager로부터 command를 수집받아서 수집 하는 기능 차단 여부.
		 *	@return true : 수집 가능, false : 수집 차단.
		 */
		bool isPassive();
		/**
		 *	ACTIVE 메시지 수집 여부를 판단하는 메쏘드.
		 *	@return true : 수집, false : 수집 차단.
		 */
		bool isReportable();
		/**
		 *	EVENT 수집 여부를 판단하는 메쏘드.
		 *	@return true : 수집, false : 수집 차단.
		 */
		bool isEnableEvent();

		/**
		 *	item 개체 정보를 프린트하는 메쏘드
		 */
		void printItem()
		{
			std::cout << "code : " << m_code ;
			std::cout << ", name : " << m_name ;
			std::cout << ", schedule : " << m_schedule ;
			std::cout << ", eschedule : " << m_eventSchedule ;
			std::cout << ", enable : " << m_enable ;
			std::cout << ", method : " << m_method << std::endl;
		}

	private:
		std::string m_code;				/**< item code */
		std::string m_name;				/**< item description */
		unsigned long m_schedule;		/**< 정보 수집 주기 */
		unsigned long m_eventSchedule;	/**< 장애 정보 수집 주기 */
		std::string m_enable;			/**< 정보 수집 차단 상태 */
		std::string m_method;			/**< 정보 수집 차단 상세 상태(ACTIVE/PASSIVE/EVENT) */
		CQueue *m_instQ;				/**< ITEM INSTANCE를 저장하는 리스트 큐 */
		CQueue *m_condQ;				/**< ITEM CONDITION를 저장하는 리스트 큐 */
		CQueue *m_alarmInstanceQ;		/**< 현재 장애 상태 정보를 저장하는 리스트 큐 */

		time_t m_collect;				/**< 정보 수집 시간 */
		time_t m_eventCollect;			/**< 장애 정보 수집 시간 */

		bool m_isCollect;				/**< 현재 정보 수집 여부 */
};


void deleteCItem(void *d);

#endif /* _CITEM_H__ */
