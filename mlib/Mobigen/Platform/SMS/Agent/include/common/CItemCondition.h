

#ifndef _CITEMCONDITION_H__
#define _CITEMCONDITION_H__ 1

#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <ctype.h>

#define MAX_COND_COUNT 20

#define COND_OPCODE_EGT '1'
#define COND_OPCODE_GT	'2'
#define COND_OPCODE_ELT	'3'
#define COND_OPCODE_LT	'4'
#define COND_OPCODE_NEQ	'5'
#define COND_OPCODE_EQ	'6'
#define COND_OPCODE_SUBSTR	'7'
#define COND_OPCODE_NSUBSTR	'8'


/**
 *	장애(임계치) 판단 조건 및 기준 값을 저장하는 구조체.
 *	OPCODE : >=, >, <=, <, !=, ==, <<, >>등의 OPERATION CODE.
 *	TYPE : double, string 등의 기준 값 유형.
 *	val : 조건 판단 기준값.
 */
typedef struct st_conditem
{
	char opcode;
	char type;
	union {
		double d;
		char s[1024];
	}val;
}st_conditem;

/**
 *	장애 판단 조건을 저장하는 구조체.
 *	COUNT : 장애 판단 조건 개수.
 *	C : AND, OR 등의 연산 조건.
 *	ITEM : 상세 판단 조건. st_conditem 값.
 */
typedef struct st_condition
{
	int count;
	char c[MAX_COND_COUNT];
	st_conditem item[MAX_COND_COUNT];
}st_condition;


//! 장애 임계치를 판단하는 조건을 저장하는 정보 개체.
/**
 *	condition id, 장애 등급(severity or level), 임계치 판단 대상(element), instance(판단 대상 instance)
 *	임계치 판단 조건(condition) 정보를 관리하는 클래스.
 *	현재는 CPUPerf, NetworkPerf에, LogCheck item에 대해서만 적용가능한다.
 *	scagent.xml 파일에서 당음과 같은 형식으로 저장된 정보를 기록한다.
 *	<conditions>
 *		<condition id="1" instance="ALL" element="1" level="Major">&gt;=5</condition>
 *	</conditions>
 */
class CItemCondition
{
	public:
		/** 생성자 */
		CItemCondition();
		/** 소멸자 */
		virtual ~CItemCondition();
		/**
		 *	condition id를 얻어오는 메쏘드.
		 *	@return condition id.
		 */
		unsigned int getIndex() { return m_index; }
		/**
		 *	element 번호를 얻어오는 메쏘드.
		 *	element는 장애 판단 대상 항목의 번호를 의미하며, 
		 *	각 항목의 번호는 COL명령으로 데이터를 조회할 경우에
		 *	얻어지는 데이터의 테이블의 헤더 순서대로 부여된다.
		 *	@return element number.
		 */
		unsigned int getElement() { return m_element; }
		/**
		 *	장애 임계치 판단 대상 개체명을 반환하는 메쏘드.
		 *	@return instance name.
		 */
		std::string getInstanceName() { return m_instName; }
		/**
		 *	장애 임계치 판단 조건을 반환하는 메쏘드.
		 *	전체 instance는 "ALL"로 설정하면 된다.
		 *	@return 임계치 판단 조건.
		 */
		std::string getCondition() { return m_condition; }
		/**
		 *	장애 등급 정보를 반환하는 메쏘스.
		 *	설정된 장애 등급('Critical', 'Major', 'Minor', 'Warning', 'Undeterminate')을 반환한다.
		 *	@return alarm severity.
		 */
		std::string getSeverity() { return m_severity; }

		/**
		 *	condition id를 설정하는 메쏘드.
		 *	@param condition id.
		 */
		void setIndex(unsigned int index) { m_index = index; }
		/**
		 *	element number를 설정하는 메쏘드.
		 *	@param element number.
		 */
		void setElement(unsigned int element) { m_element = element; }
		/**
		 *	Instance 명을 설정하는 메쏘드.
		 *	모든 Instance인 경우에는 "ALL"로 설정하면 된다.
		 *	@param instance name.
		 */
		void setInstanceName(std::string instName) { m_instName = instName; }
		/**
		 *	임계치 판단 조건을 설정하는 메쏘드.
		 *	장애 발생 조건(임계치)을 설정한다.
		 *	@param 임계치 판단 조건.
		 */
		void setCondition(std::string condition) { m_condition = condition; }
		/**
		 *	장애 등급을 설정하는 메쏘드.
		 *	장애 등급('Critical', 'Major', 'Minor', 'Warning', 'Undeterminate' 등)을 설정한다.
		 *	@param alarm severity.
		 */
		void setSeverity(std::string severity) { m_severity = severity; }
		/**
		 *	장애 발생 여부를 판단하는 메쏘드.
		 *	주어진 값을 임계치 판단 조건과 비교하여 장애 발생 여부를 판단한다.
		 *	@param 수집된 정보 unsigned integer value.
		 *	@return true : 임계치 초과 혹은 장애 발생, false : 임계치 미달 혹은 장애 해지. 
		 */
		bool isOverThreshold(unsigned int value) { return isOverThreshold((unsigned long) value); }
		/**
		 *	장애 발생 여부를 판단하는 메쏘드.
		 *	주어진 값을 임계치 판단 조건과 비교하여 장애 발생 여부를 판단한다.
		 *	@param 수집된 정보 unsigned long value.
		 *	@return true : 임계치 초과 혹은 장애 발생, false : 임계치 미달 혹은 장애 해지. 
		 */
		bool isOverThreshold(unsigned long value);
		/**
		 *	장애 발생 여부를 판단하는 메쏘드.
		 *	주어진 값을 임계치 판단 조건과 비교하여 장애 발생 여부를 판단한다.
		 *	@param 수집된 정보 integer value.
		 *	@return true : 임계치 초과 혹은 장애 발생, false : 임계치 미달 혹은 장애 해지. 
		 */
		bool isOverThreshold(int value);
		/**
		 *	장애 발생 여부를 판단하는 메쏘드.
		 *	주어진 값을 임계치 판단 조건과 비교하여 장애 발생 여부를 판단한다.
		 *	@param 수집된 정보 long value.
		 *	@return true : 임계치 초과 혹은 장애 발생, false : 임계치 미달 혹은 장애 해지. 
		 */
		bool isOverThreshold(long value);
		/**
		 *	장애 발생 여부를 판단하는 메쏘드.
		 *	주어진 값을 임계치 판단 조건과 비교하여 장애 발생 여부를 판단한다.
		 *	@param 수집된 정보 double value.
		 *	@return true : 임계치 초과 혹은 장애 발생, false : 임계치 미달 혹은 장애 해지. 
		 */
		bool isOverThreshold(double value);
		/**
		 *	장애 발생 여부를 판단하는 메쏘드.
		 *	주어진 값을 장애 판단 조건과 비교하여 장애 발생 여부를 판단한다.
		 *	@param 수집된 정보 string value.
		 *	@return true : 장애 발생, false : 장애 해지. 
		 */
		bool isOverThreshold(std::string cond);
		/**
		 *	장애 발생 여부를 판단하는 메쏘드.
		 *	주어진 값을 장애 판단 조건과 비교하여 장애 발생 여부를 판단한다.
		 *	@param 수집된 정보 character value.
		 *	@return true : 장애 발생, false : 장애 해지. 
		 */
		bool isOverThreshold(char *value);
		/**
		 *	주어진 문자열에서 연산자(>=, >, <=, <, ==, !=, <<, >>)를 파싱한다.
		 *	@param 임계치 판단 조건식.
		 *	@return true : parsing success, false : parsing fail.
		 */
		bool checkOperator(char *pcmd);
		/**
		 *	주어진 값(double)과 임계치 조건(st_conditem)을 비교하여 장애 발생 여부를 판단하는 메쏘드.
		 *	@param 개발 장애 임계치 판단 조건.
		 *	@param 수집된 정보(double)
		 *	@return true : 장애 발생, false : 장애 해지.
		 */
		bool checkCondition(st_conditem *item, double val);
		/**
		 *	주어진 문자열과 임계치 조건(st_conditem)을 비교하여 장애 발생 여부를 판단하는 메쏘드.
		 *	@param 개발 장애 임계치 판단 조건.
		 *	@param 수집된 정보(문자열)
		 *	@return true : 장애 발생, false : 장애 해지.
		 */
		bool checkCondition(st_conditem *item, char *val);
		/**
		 *	임계치 판단 조건이 여러 조건의 논리 연산(AND, OR)의 조합으로 이루어진 경우
		 *	주어진 값(double)과 임계치 조건을 비교 판단한 결과값과 이전에 연산 결과을 논리 연산(AND, OR)한 결과를 반환하는 메쏘드.
		 *	@param 이전 임계치 판단 결과값.
		 *	@param 논리 연산자(AND, OR).
		 *	@param 임계치 판단 조건.
		 *	@param 수집된 정보(double).
		 *	@return true : 장애 발생, false : 장애 해지.
		 */
		bool checkCondition(bool b, char op, st_conditem *item, double val);
		/**
		 *	임계치 판단 조건이 여러 조건의 논리 연산(AND, OR)의 조합으로 이루어진 경우
		 *	주어진 문자열과 임계치 조건을 비교 판단한 결과값과 이전에 연산 결과을 논리 연산(AND, OR)한 결과를 반환하는 메쏘드.
		 *	@param 이전 임계치 판단 결과값.
		 *	@param 논리 연산자(AND, OR).
		 *	@param 임계치 판단 조건.
		 *	@param 수집된 정보(문자열).
		 *	@return true : 장애 발생, false : 장애 해지.
		 */
		bool checkCondition(bool b, char op, st_conditem *item, char *val);
		/**
		 *	주어진 임계치 판단 조건을 parsing하여 m_parsecondition 변수에 상세 정보를 기록하는 메쏘드.
		 *	실제 장애 판단은 m_parsecondition에 주어진 조건과 비교 판단하여 장애 발생 여부를 판단한다.
		 *	@param 임계치 판단 조건식.
		 */
		void parseCondition(char *msg);

		/**
		 *	판단조건식이 변경되는 경우 다시 파스하도록 reset한다.
		 *	@param void
		 *  @return void
		 */
		void setChange() { isChange = true; }

	private:
		unsigned int m_index;				/**< condition id */
		unsigned int m_element;				/**< element number */
		std::string m_instName;				/**< instance name */
		std::string m_condition;			/**< 임계치 판단 조건식 */
		std::string m_severity;				/**< 장애 등급 */
		st_condition m_parsecondition;		/**< 구문 분석된 임계치 판단 조건식 */
		bool isChange;						/**< 임계치가 변경된 경우 다시 분석하는 플래그 */
};

void deleteCItemCondition(void *d);

#endif /* _CITEMCONDITION_H__ */
