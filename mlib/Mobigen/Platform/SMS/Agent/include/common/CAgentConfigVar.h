
#ifndef _CAGENTCONFIGVAR_H__
#define _CAGENTCONFIGVAR_H__

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <pthread.h>
#include <unistd.h>
#include <string>

#include "MD5LIB.h"
#include "MD5.h"

#include "tinyxml.h"
#include "CItem.h"

//! scagent.xml 파일로부터 환경 설정 정보 및 Item Code 정보를 로딩하여 관리하는 클래스
/*!
 *	Item Code 정보를 읽어서 CItem class에 저장하고 관리하며, 
 *	기타 오라클 로그인에 필요한 계정, 
 *	SMS Manager와 통신하기 위한 리슨 포트 및 
 *	SMS Agent로 로그인하기 위한 계정 및 접속 허용 아이피 정보를 관리한다.
*/
class CAgentConfigVar
{
	public:
		//! 생성자
		/*! Detail : */
		CAgentConfigVar();
		//! 소멸자.
		/*! Detail : */
		virtual ~CAgentConfigVar();
		//! scagent.xml 파일을 로딩하는 함수.
		/*! xml 파일로부터 Item Code 및 기타 환경 정보를 로딩한다. */
		void loadXMLConfigVar();
		//! 주어진 Item Code에 해당한는 Item 정보를 얻어오는 함수.
		/*!
			\param a charater pointer.
			\return return CItem class, if failed return NULL.
			\sa CItem
		*/
		CItem *getItem(char *code){
			std::string strcode = code;
			return getItem(strcode); }

		//! 주어진 Item Code에 해당한는 Item 정보를 얻어오는 함수.
		/*!
			\param a string value
			\return return CItem class, if failed return NULL.
			\sa CItem class.
		*/
		CItem *getItem(std::string code);

		//! 특정 Item을 추가하는 함수.
		/*!
			\param CItem pointer.
			\sa CItem.
		*/
		void addItem(CItem *item);
		//! 특정 Item의 내용을 변경하는 함수.
		/*!
			\param CItem pointer.
			\sa CItem.
		*/
		void setItem(CItem *item);
		//! 특정 Item의 내용을 삭제하는 함수.
		/*!
			\param string item code name.
		*/
		void delItem(std::string code);
		/** Item list를 반환하는 함수.
		 *	현재 SMS Agent가 관리하고 있는 CItem class(item code)를 저장하고 있는 리스트 큐.를 반환하여 준다.
		 *	@return CQueue pointer.
		*/
		CQueue *getItemQ();
		//! scagent.xml 파일을 업데이트하는 함수.
		/*!
			현재 SMS Agent가 관리하고 있는 item code 및 환경 설정 정보를 scagent.xml파일로 저장하는 함수이다.
		*/
		void unloadXMLConfigVar();

		/**
		 *	XML Document(m_doc)에 특정 item code를 추가하는 함수.
		 *	@param CItem class
		 *	@return 추가된 XML Element pointer.
		 */
		TiXmlElement *makeXmlElement(CItem *item);

		/**
		 *	주어진 name에 해당하는 XML Element를 생성하여, 
		 *	해당 element에 첫번째 인자인 str XML Text를 생성하여 추가한 후
		 *	XML Element XML Document(m_doc)에 추가한다.
		 *	example) <instance name="test" /> 인 경우, name = name, test = str 이 된다.
		 *	@param 추가될 XML Text에 들어갈 내용(string).
		 *	@param 본 내용이 추가될 XML Element.
		 *	@param 추가될 XML Element의 Title. 
		 */
		void linkEndChild(std::string str, TiXmlElement *elem, const char *name);

		/**
		 *	주어진 name에 해당하는 XML Element를 생성하여, 
		 *	해당 element에 첫번째 인자인 str XML Text를 생성하여 추가한 후
		 *	XML Element XML Document(m_doc)에 추가한다.
		 *	example) <instance name="0" /> 인 경우, name = name, 0 = l 이 된다.
		 *	@param 추가될 XML Text에 들어갈 내용(unsigned long).
		 *	@param 본 내용이 추가될 XML Element.
		 *	@param 추가될 XML Element의 Title. 
		 */
		void linkEndChild(unsigned long l, TiXmlElement *elem, const char *name);

		/**
		 *	주어진 코드에 해당하는 item을 XML Document에서 삭제한다.
		 *	@param 삭제할 item code.
		 */
		void removeDocItem(std::string code);
		
		/**
		 *	SMS Agent가 수집하는 장애 정보를 SMS Manager로 전송하기 위한 리슨 포트를 반환하는 함수.
		 *	@return TCP/IP Alarm listen port.
		 */
		int getEventPort(){ return m_eventport; }

		/**
		 *	SMS Agent가 수집하는 단기(1시간 이하) 성능 정보를 SMS Manager로 전송하기 위한 리슨 포트를 반환하는 함수.
		 *	@return TCP/IP short period Performance listen port.
		 */
		int getShortPerfPort() { return m_shortperfport; }

		/**
		 *	SMS Agent가 수집하는 중장기(1시간 이상) 성능 정보를 SMS Manager로 전송하기 위한 리슨 포트를 반환하는 함수.
		 *	@return TCP/IP long period Performance listen port.
		 */
		int getLongPerfPort() { return m_longperfport; }

		/**
		 *	SMS Manager로부터 전달받은 명령을 수행한 결과값을 SMS Manager로 전송하기 위한 리슨 포트를 반환하는 함수.
		 *	@return TCP/IP command response listen port.
		 */
		int getRespPort() { return m_respport; }

		/**
		 *	SMS Manager로부터 명령을 전달받기 위한 리슨 포트를 반환하는 함수.
		 *	@return TCP/IP command listen port.
		 */
		int getCmdPort() { return m_cmdport; }

		/**
		 *	SMS Manager와 SMS Agent간의 연결된 세션 상태 및 각 세션별 누적 메시지 정보를 전송하기 위한 리슨 포트를 반환하는 함수.
		 *	@return TCP/IP listen port to get session status.
		 */
		int getSessionPort() { return m_sessionport; }
		
		/**
		 *	SMS Agent로 접속하기 위한 계정 정보를 반환하는 함수.
		 *	@return SMS Agent user id.
		 */
		std::string getUserid() { return m_userid; }

		/**
		 *	SMS Agent로 접속하기 위한 패스워드 정보를 반환하는 함수.
		 *	@return SMS Agent access password.
		 */
		std::string getPasswd() { return m_passwd; }

		/**
		 *	SMS Agent로 접속이 허용된 IP 대역 정보를 반환하는 함수.
		 *	@return permmitted access ip address.
		 */
		std::string getAccessIP() { return m_accessip; }
		
		/**
		 *	Database Type 정보를 반환하는 함수.
		 *	@return Database type
		 */
		std::string getDBType() { return m_dbtype; }

		/**
		 *	Oracle system 계정을 반환하는 함수.
		 *	@return Oracle system account.
		 */
		std::string getOraUID() { return m_orauid; }

		/**
		 *	Oracle system 계정의 암호를 반환하는 함수.
		 *	@return Oracle system account password.
		 */
		std::string getOraPasswd() { return m_orapasswd; }
		
		/**
		 *	Oracle SID 정보를 반환하는 함수.
		 *	@return Oracle SID.
		 */
		std::string getOraSID() { return m_orasid; }

		/**
		 *	method for setting database type
		 *	@param database type name
		 */
		void setDBType(char *dbtype) { m_dbtype = dbtype; }

		/**
		 *	method for setting oracle system account.
		 *	@param oracle system account user id.
		 */
		void setOraUID(char *uid) { m_orauid = uid; }

		/**
		 *	method for setting oracle SID.
		 *	@param oracle SID.
		 */
		void setOraSID(char *sid) { m_orasid = sid; }

		/**
		 *	method for setting oracle system account password.
		 *	@param oracle system account password.
		 */
		void setOraPasswd(char *passwd) { m_orapasswd = passwd; }

		/**
		 *	method for setting SMS Agent account user id.
		 *	@param SMS Agent account user id.
		 */
		void setUserid(char *userid) { m_userid = userid; }

		/**
		 *	method for setting SMS Agent account password.
		 *	@param SMS Agent password.
		 */
		void setPasswd(char *passwd) { m_passwd = passwd; }

		/** 
		 *	method for setting permmitted ip address to access SMS Agent.
		 *	@param permmitted ip address range(ex : 127.0.0.*)
		 */
		void setAccessIP(char *accessip) { m_accessip = accessip; }
		
		/**
		 *	주어진 userid에 해당하는 SMS Agent의 password 및 접속 허용 ip address를 설정하는 함수.
		 *	@param SMS Agent account user id.
		 *	@param SMS Agent account password.
		 *	@param permmitted ip address range.
		 */
		bool setUserInfo(std::string sid, std::string userid, std::string password);
		
		/**
		 * method for locking.
		 */
		void lock();

		/** method for unlocking */
		void unlock();

	private:
		TiXmlDocument *m_doc;	/**< scagent.xml 파일로부터 로딩한 item 및 환경 설정 정보를 저장하고 있는 XML Document */
		CQueue *m_itemQ;		/**< 로딩한 CItem class를 저장하고 있는 리스트 클래스 */
		int m_eventport;		/**< SMS Agent에서 발생하는 장애 정보를 전송하기 위한 포트 */
		int m_shortperfport;	/**< SMS Agent에서 수집되는 단기(1시간 이하) 성능 정보를 전송하기 위한 포트 */
		int m_longperfport;		/**< SMS Agent에서 수집되는 중장기(1시간 이상) 성능 정보를 전송하기 위한 포트 */
		int m_respport;			/**< SMS Manager로부터 전달받은 명령을 수행한 결과를 전송하기 위한 포트 */
		int m_cmdport;			/**< SMS Manager로부터 명령 코드를 전달받는 포트 */
		int m_sessionport;		/**< 현재 SMS Agent에 접속된 세션 정보 및 각 세션별 누적 메시지 정보를 조회하기 위한 포트 */
		std::string m_dbtype;	/**< Database type 정보 */
		std::string m_orauid;	/**< 오라클 접속 user id(system 계정) */
		std::string m_orapasswd; /**< 오라클 접속 패스워드 */
		std::string m_orasid;	/**< 오라클 SID */
		std::string m_userid;	/**< SMS Agent 접속 계정 */
		std::string m_passwd;	/**< SMS Agent 접속 패스워드 */
		std::string m_accessip; /**< SMS Manager의 접속 허용 IP 주소 */
		pthread_mutex_t m_lock; /**< CAgentConfigVar 클래스 정보 관리에 따른 동기화 변수 */

};

#endif /* _CAGENTCONFIGVAR_H__ */
