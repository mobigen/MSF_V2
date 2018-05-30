
#ifndef __CPROTOCOLPROCESSOR_H__
#define __CPROTOCOLPROCESSOR_H__ 1

#include <stdio.h>
#include <stdlib.h>
#include <string>

#include "CAgentEnvVar.h"
#include "CRegex.h"
#include "CMisc.h"
#include "CMessageFormatter.h"
#include "CPolicyItem.h"

#define OPCODE_COL 1
#define OPCODE_GET 2
#define OPCODE_SET 3
#define OPCODE_GETCOND 4
#define OPCODE_SETCOND 5
#define OPCODE_ADDCOND 6
#define OPCODE_DELCOND 7
#define OPCODE_COLINST 8
#define OPCODE_GETINST 9
#define OPCODE_SETINST 10
#define OPCODE_ADDINST 11
#define OPCODE_DELINST 12

#define MAX_ATTRIBUTE_NUM 20

#define STR_COMMAND_PATTERN "((COL)|(GET)|(SET)|(COLINST)|(GETINST)|(SETINST)|(ADDINST)|(DELINST)|(GETCOND)|(SETCOND)|(ADDCOND)|(DELCOND)):CODE=[0-9a-zA-Z]+.*"

#define SC_ITEM_CODE_USERINFO				"UserInfo"
#define SC_ITEM_ATTR_USERID 				"userid"
#define SC_ITEM_ATTR_PASSWD 				"passwd"
#define SC_ITEM_ATTR_ACCESSIP 				"accessip"

#define SC_ITEM_ATTR_SCHEDULE 				"schedule"
#define SC_ITEM_ATTR_EVENT_SCHEDULE 		"eschedule"
#define SC_ITEM_ATTR_ENABLE 				"enable"
#define SC_ITEM_ATTR_METHOD 				"method"
#define SC_ITEM_ATTR_LEVEL 					"level"
#define SC_ITEM_ATTR_ELEMENT 				"element"
#define SC_ITEM_ATTR_INSTANCE 				"INST"
#define SC_ITEM_ATTR_CONDITION 				"COND"
#define SC_ITEM_ATTR_CONDITIONID 			"CONDID"

/**
 *	수집 요청 명령어의 수집 개별 파라미터값(param_name=value)을 저장하는 구조체
 */
typedef struct _st_attribute {
	std::string name;
	std::string value;
}st_attribute;

/**
 *	수집 요청 명령어를 파싱하여 명령 코드, item 코드, item parameter값 등의 정보를 저장하는 구조체.
 */
typedef struct _st_cmd {
	unsigned int opcode;
	std::string itemcode;
	int attr_num;
	st_attribute attr[MAX_ATTRIBUTE_NUM];
}st_cmd;

//!	SMS Manager로부터 수신된 명령 코드를 구문 분석하고 처리하는 클래스.
/**
 *	SMS Manager로부터 수신된 명령 코드가 정해진 syntax에 맞는지 검사하고,
 *	정해진 규약에 따른 명령 코드를 분석하여, 요청 되어진 명령어를 처리하는 클래스.
 */
class CProtocolProcessor
{
	public:
		/**
		 *	생성자\n
		 *	명령 코드에 대한 정규 표현식을 초기화한다.
		 */
		CProtocolProcessor(){ m_reg = new CRegex(STR_COMMAND_PATTERN); }
		/**
		 * 소멸자
		 */
		~CProtocolProcessor(){ delete m_reg; }
		/**
		 *	SMS Manager로부터 요청된 명령 코드를 분석 및 처리하는 최상위 메쏘드.
		 *	@param command message(수신된 명령어).
		 */
		void process(char *pcmd);
		/**
		 *	SMS Manager로부터 수신된 명령 코드에 따라 분기 처리하는 메쏘드.
		 *	@param command message(수신된 명령어).
		 */
		void execute(char *pcmd);
		/**
		 *	SMS Manager로부터 "COL" 명령 코드로 요청된 경우 이를 처리하는 메쏘드.
		 *	@param command message(수신된  명령어).
		 */
		void execCOL(char *pcmd);
		/**
		 *	SMS Manager로부터 "GET" 명령 코드로 요청된 경우 이를 처리하는 메쏘드.
		 *	@param command message(수신된  명령어).
		 */
		void execGET(char *pcmd);
		/**
		 *	SMS Manager로부터 "SET" 명령 코드로 요청된 경우 이를 처리하는 메쏘드.
		 *	@param command message(수신된  명령어).
		 */
		void execSET(char *pcmd);
		/**
		 *	SMS Manager로부터 "GETINST" 명령 코드로 요청된 경우 이를 처리하는 메쏘드.
		 *	@param command message(수신된  명령어).
		 */
		void execGETINST(char *pcmd);
		/**
		 *	SMS Manager로부터 "SETINST" 명령 코드로 요청된 경우 이를 처리하는 메쏘드.
		 *	@param command message(수신된  명령어).
		 */
		void execSETINST(char *pcmd);
		/**
		 *	SMS Manager로부터 "ADDINST" 명령 코드로 요청된 경우 이를 처리하는 메쏘드.
		 *	@param command message(수신된  명령어).
		 */
		void execADDINST(char *pcmd);
		/**
		 *	SMS Manager로부터 "DELINST" 명령 코드로 요청된 경우 이를 처리하는 메쏘드.
		 *	@param command message(수신된  명령어).
		 */
		void execDELINST(char *pcmd);
		/**
		 *	SMS Manager로부터 "GETCOND" 명령 코드로 요청된 경우 이를 처리하는 메쏘드.
		 *	@param command message(수신된  명령어).
		 */
		void execGETCOND(char *pcmd);
		/**
		 *	SMS Manager로부터 "SETCOND" 명령 코드로 요청된 경우 이를 처리하는 메쏘드.
		 *	@param command message(수신된  명령어).
		 */
		void execSETCOND(char *pcmd);
		/**
		 *	SMS Manager로부터 "ADDCOND" 명령 코드로 요청된 경우 이를 처리하는 메쏘드.
		 *	@param command message(수신된  명령어).
		 */
		void execADDCOND(char *pcmd);
		/**
		 *	SMS Manager로부터 "DELCOND" 명령 코드로 요청된 경우 이를 처리하는 메쏘드.
		 *	@param command message(수신된  명령어).
		 */
		void execDELCOND(char *pcmd);
		/**
		 *	SMS Manager로부터 "SET" 명령 중에서 ITEM CODE가 "UserInfo"인 경우\n
		 *	SMS Agent 계정 설정을 처리하는 메쏘드.
		 *	@param command message(수신된  명령어).
		 */
		void setUserInfo(char *pcmd);
		/**
		 *	SMS Manager로부터 수신된 명령어가 정해진 규약에 맞는지 검사하고\n
		 *	파싱하는 메쏘드.
		 *	@param command message(수신된 명령어)
		 *	@return 파싱된 명령어.
		 */
		char * parse(char *pcmd);
		/**
		 *	SMS Agent가 기동하는데 필요한 환경 정보 및 item 정보를 관리하는 객체를 저장하는 메쏘드.
		 *	@param CAgentEnvVar pointer.
		 *	@see CAgentEnvVar, CAgentConfigVar.
		 */
		void setEnvVar(CAgentEnvVar *var){ m_envvar = var; }
		/**
		 *	SMS Agent가 기동하는데 필요한 환경 정보 및 item 정보를 관리하는 객체를 조회하는 메쏘드.
		 *	@return CAGentEnvVar pointer.
		 *	@see CAgentEnvVar, CAgentConfigVar.
		 */
		CAgentEnvVar* getEnvVar(){ return m_envvar; }

	private:
		CRegex *m_reg;				/**< 명령어를 파싱할 정규 표현식에 대한 정보를 저장하는 객체 */
		CAgentEnvVar *m_envvar;		/**< 환경 정보를 저장하는 객체 */
		st_cmd m_cmd;				/**< 구문 분석된 명령어 구조체 */
		std::string m_itemcode;		/**< item code 정보 */
		/**
		 *	명령어를 파싱하여 구문 분석된 명령어 구조체에 저장하는 메쏘드.
		 *	@param command message(수신된 명령어).
		 *	@return false : syntax error, else true
		 */
		bool parseCommand(char *);
};

#endif /* __CPROTOCOLPROCESSOR_H__ */
