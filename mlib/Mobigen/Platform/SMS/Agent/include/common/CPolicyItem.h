

#ifndef __CPOLICYITEM_H__
#define __CPOLICYITEM_H__ 1


#include "CAgentEnvVar.h"
#include "CMessageFormatter.h"


//! 스케쥴러에 의해 수집 쓰레드에 수집 요청을 할때 필요한 정책 정보를 관리하는 클래스.
/**
 *	수집 요청 item, 수집 유형, 수집 시간, 수집 명령어 등의 정보를 담고 있는 정보 클래스이다.
 */
class CPolicyItem 
{
	public:
		/** 생성자 */
		CPolicyItem() { m_instQ = new CQueue; }
		/** 소멸자 */
		~CPolicyItem() { delete m_instQ; }
		/** 
		 *	수집 시간 정보를 설정하는 메쏘드 
		 *	@param 수집 시간.
		 */
		void setPollTime(time_t t){ m_polltime = t; }
		/**
		 *	item 정보를 설정하는 메쏘드.
		 *	@param CItem pointer.
		 */
		void setItem(CItem *item) { m_item = item; }
		/**
		 *	수집 유형 정보를 설정하는 메쏘드. 수집 유형(TYPE_PASSIVE, TYPE_ACTIVFE, TYPE_EVENT)
		 *	@param 수집 유형(TYPE_PASSIVE, TYPE_ACTIVFE, TYPE_EVENT)
		 */
		void setPollType(unsigned int type) { m_polltype = type; }
		/**
		 *	수집시간 정보를 조회하는 메쏘드.
		 *	@return 수집 시간(seconds)
		 */
		time_t getPollTime() { return m_polltime; }
		/**
		 *	수집 item 클래스를 조회하는 메쏘드.
		 *	@return CItem pointer.
		 *	@see CItem
		 */
		CItem *getItem() { return m_item; }
		/**
		 *	수집 유형 정보를 조회하는 메쏘드.
		 *	@return 수집 유형(TYPE_PASSIVE, TYPE_ACTIVFE, TYPE_EVENT)
		 */
		unsigned int getPollType() { return m_polltype; }
		/**
		 *	수집 대상 인스턴스 정보를 조회하는 메쏘드.\n
		 *	인스턴스가 없을 경우는 조회 가능한 모든 인스턴스를 조회한다.
		 *	@return CQueue pointer(instance queue)
		 */
		CQueue *getInstQ() { return m_instQ; }
		/**
		 *	SMS Manager에 의해 수집 요청된 경우 수집 요청된 명령어를 설정하는 메쏘드.
		 *	@param command(수집 요청 명령어)
		 */
		void setCommand(char *cmd) { m_cmd = cmd; }
		/**
		 *	SMS Manager에 의해 수집 요청된 경우 수집 요청된 명령어를 조회하는 메쏘드.
		 *	@return command(수집 요청 명령어)
		 */
		std::string getCommand() { return m_cmd; }

	private:
		std::string m_cmd;			/**< 수집 요청 명령어 */
		time_t m_polltime;			/**< 수집 시간 */
		unsigned int m_polltype;	/**< 수집 유형 */
		CItem *m_item;				/**< 수집 item */
		CQueue *m_instQ;			/**< 수집 대상 인스턴스 정보 큐 */
};

#endif /* __CPOLICYITEM_H__ */
