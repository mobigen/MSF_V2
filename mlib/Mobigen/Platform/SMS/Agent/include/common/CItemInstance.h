


#ifndef __CITEMINSTANCE_H__
#define __CITEMINSTANCE_H__ 1

#include <stdio.h>
#include <stdlib.h>
#include <string>

#include "CQueue.h"


//! Item의 Instance 정보를 관리하는 클래스.
/**
 *	Instance name, Instance value 정보를 관리한다.
 *	현재 Instance name, Instance value은 같은 정보로 설정 관리되어야 한다.
 *	scagent.xml 파일에서 당음과 같은 형식으로 저장된 정보를 기록한다.
 *	<instances>
 *		<instance name="test">test</instance>
 *	</instances>
 */
class CItemInstance
{
	public:
		/** 생성자 */
		CItemInstance();
		/** 소멸자 */
		virtual ~CItemInstance();
		/**
		 *	Instance 명을 반환하는 메쏘드.
		 *	@return instance name.
		 */
		std::string getName() { return m_name; }
		/**
		 *	Instance 값을 반환하는 메쏘드.
		 *	@return instance value.
		 */
		std::string getValue() { return m_value; }
		/**
		 *	데이터 저장소를 반환하는 메쏘드.
		 *	@return CQueue pointer.
		 */
		CQueue *getDataQ() { return m_dataQ; }
		/**
		 *	Instance name을 설정하는 메쏘드.
		 *	@param instance name.
		 */
		void setName(char *name) { m_name = name; }
		/**
		 *	Instance value를 설정하는 메쏘드.
		 *	@param instance value.
		 */
		void setValue(char *value) { m_value = value; }
		/**
		 *	Instance name을 설정하는 메쏘드.
		 *	@param instance name.
		 */
		void setName(std::string name) { m_name = name; }
		/**
		 *	Instance value를 설정하는 메쏘드.
		 *	@param instance value.
		 */
		void setValue(std::string value) { m_value = value; }

	private:
		std::string m_name;		/**< instance name */
		std::string m_value;	/**< instance value */

		CQueue *m_dataQ; /**< 내부적으로 데이터를 저장하기 위한 데이터 큐 */
};

void deleteCItemInstance(void *d);

#endif /* __CITEMINSTANCE_H__ */
