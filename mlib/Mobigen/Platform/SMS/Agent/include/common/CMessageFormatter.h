

#ifndef __CMESSAGEFORMATTER_H__
#define __CMESSAGEFORMATTER_H__ 1

#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <unistd.h>
#include <sys/time.h>
#include <time.h>


#include "CItem.h"


#define TYPE_PASSIVE 1
#define TYPE_EVENT 2
#define TYPE_ACTIVE 3


//! 수집된 메시지를 SMS Manager와 규약된 메시지 포맷으로 변환하는 클래스.
/**
 *	메시지 유형에 따라 다음 3가지 포맷으로 변환시킨다.
 *		-# PASSIVE :\n
 *			${HOSTNAME} YYYY-MM-DD HH:MI:SS\n
 *			${ITEM_CODE} ${ITEM_DESCRIPTION}\n
 *			PASSIVE	${COMMAND}\n
 *			${DATA HEADER}\n
 *			${DATA}\n
 *			COMPLETED\n
 *		-# ACTIVE :\n
 *			${HOSTNAME} YYYY-MM-DD HH:MI:SS\n
 *			${ITEM_CODE} ${ITEM_DESCRIPTION}\n
 *			ACTIVE\n
 *			${DATA HEADER}\n
 *			${DATA}\n
 *			COMPLETED\n
 *		-# EVENT :\n
 *			${HOSTNAME} YYYY-MM-DD HH:MI:SS\n
 *			${ITEM_CODE} ${ITEM_DESCRIPTION}\n
 *			EVENT ${CONDITION} ${ELEMENT} ${SEVERITY} ${START/END}\n
 *			${DATA HEADER}\n
 *			${DATA}\n
 *			COMPLETED\n
 */
class CMessageFormatter
{
	public:
		/** 생성자 */
		CMessageFormatter();
		/** 소멸자 */
		~CMessageFormatter();
		/**
		 *	수집 시간을 설정하는 메쏘드.
		 *	@param 수집 시간.
		 */
		void setPollTime(time_t polltime) { m_polltime = polltime; }
		/**
		 *	수집하는 item(CItem) 정보를 설정하는 메쏘드.
		 *	@param CItem pointer.
		 *	@see CItem.
		 */
		void setItem(CItem *item){ m_item = item; }
		/**
		 *	데이터의 수집 항목에 대한 Header 정보를 설정하는 메쏘드.
		 *	@param 수집 항목 header 정보.
		 */
		void setTitle(char *title) { m_title = title; }
		/**
		 *	PASSIVE에 의한 데이터 수집인 경우, SMS Manager로부터 전송받은 수집 명령어를 설정하는 메쏘드.
		 *	@param 수집 요청 명령어.
		 */
		void setCommand(char *cmd) { m_cmd = cmd; }
		/**
		 *	수집 유형을 설정하는 메쏘드.
		 *	@param 수집 유형(TYPE_PASSIVE/TYPE_ACTIVE/TYPE_EVENT)
		 */
		void setType(unsigned int type){ m_type = type; }
		/**
		 *	수집된 데이터가 장애 데이터인 경우에 장애 판단 조건을 설정하는 메쏘드.
		 *	@param 장애 판단 조건 클래스(CItemCondition) pointer.
		 *	@see CItemCondition
		 */
		void setItemCondition(CItemCondition *);
		/**
		 *	수집된 item code 정보를 설정하는 메쏘드.
		 *	@param item code(character).
		 */
		void setItemCode(char *code);
		/**
		 *	수집된 item code 정보를 설정하는 메쏘드.
		 *	@param item code(string).
		 */
		void setItemCode(std::string );
		/**
		 *	수집된 정보가 장애 정보인 경우 장애 발생 여부.
		 *	@param true : START, end : END.
		 */
		void setEventStatus(bool b) { m_alarm = b; }
		/**
		 *	수집된 정보를 SMS Manager로 전송하기 위한 메시지 포맷으로 변환하는 메쏘드.
		 *	@return 변환된 메시지.
		 */
		char * makeMessage();
		/**
		 *	에러 메시지를 생성하기 위한 메쏘드.
		 *	현재 의미 없음.
		 */
		std::string makeErrorMessage(char *msg);
		/**
		 *	에러 메시지를 생성하기 위한 메쏘드.
		 *	현재 의미 없음.
		 */
		std::string makeErrorMessage(std::string msg );
		/**
		 *	수집 유형 정보를 반환하는 메쏘드.
		 *	@return 수집 유형(TYPE_ACTIVE/TYPE_PASSIVE/TYPE_EVENT)
		 */
		std::string getTypeCode();
		/**
		 *	작성될 메시지를 추가하는 메쏘드.
		 *	@param 추가 메시지.
		 */
		void addMessage(char *msg) { m_msgQ.enqueue(msg, NULL); }

	private:
		bool m_alarm;			/**< 장애 발생/해지(START/END) 여부 */
		unsigned int m_type;	/**< 데이터 수집 유형(TYPE_ACTIVE/TYPE_PASSIVE/TYPE_EVENT) */
		time_t m_polltime;		/**< 데이터 수집 시간 */
		std::string m_code;		/**< ITEM CODE */
		std::string m_title;	/**< Message Title */
		std::string m_cmd;		/**< PASSIVE인 경우 수집 요청 명령어. */
		CItem *m_item;			/**< CItem */
		CItemCondition *m_cond;	/**< 장애 판단 조건 */
		CQueue m_msgQ;			/**< 메시지(데이터) 큐 */	
};

#endif /* __CMESSAGEFORMATTER_H__ */
