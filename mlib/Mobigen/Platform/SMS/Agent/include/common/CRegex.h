
#ifndef __REGEX_H__
#define __REGEX_H__

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <errno.h>
#include <regex.h>


//!	정규표현식을 처리하는 클래스.
/**
 *	특정 메시지에서 정규 표현식으로 주어진 메시지를 분석 및 파싱하는 클래스.
 */
class CRegex
{
	protected:
		regex_t	m_re; /**< 정규 패턴 정보를 지닌 키 변수 */
		char	*m_pattern;	/**< 정규 패턴식 */
		/**
		 *	정규 패턴식을 초기화하는 메쏘드.
		 *	@param 정규 패턴 키.
		 *	@param 정규 패턴 식.
		 *	@return return 1 if success, else return -1.
		 */
		int initRegex(regex_t *re, char *msg);
		/**
		 *	주어진 메시지에서 정규 패턴과 일치하는 메시지를 얻어오는 메쏘드.
		 *	얻어온 메시지는 반환받은 개체에서 메모리를 해지해 주어야 한다.
		 *	@param 정규 패턴 키.
		 *	@param 파싱 대상 메시지(문자열)
		 *	@return 파싱된 메시지.
		 */
		char* getMatchedString(regex_t *re, char *msg);
		/**
		 *	주어진 메시지에서 정규 패턴과 일치하는 메시지의 첫 번째 포인터를 얻어오는 메쏘드.
		 *	@param 정규 패턴 키.
		 *	@param 파싱 대상 메시지(문자열).
		 *	@param 정규 패턴과 일치하는 첫번째 포인터.
		 */
		char* getMatchedStartPoint(regex_t *re, char *msg);
		/**
		 *	주어진 메시지에서 정규 패턴과 일치하는 메시지의 마지막 포인터를 얻어오는 메쏘드.
		 *	@param 정규 패턴 키.
		 *	@param 파싱 대상 메시지(문자열).
		 *	@param 정규 패턴과 일치하는 마지막 포인터.
		 */
		char* getMatchedEndPoint(regex_t *re, char *msg);
		/**
		 *	주어진 메시지에서 정규 패턴과 일치하는 메시지의 정보를 얻어오는 메쏘드.
		 *	@param 정규 패턴 키.
		 *	@param 파싱 대상 메시지(문자열)
		 *	@return 정규 패턴과 일치하는 메시지의 정보
		 */
		regmatch_t* getRegMatch(regex_t *re, char *msg);
		/**
		 *	정규 패턴식을 메모리에서 해지하는 메쏘드.
		 *	@param 정규 패턴 키.
		 */
		void freeRegex(regex_t *re);

	public:
		/** 생성자 */
		CRegex(){};
		/**
		 *	생성자
		 *	@param 정규 패턴식
		 */
		CRegex(char *pattern);
		/** 소멸자 */
		~CRegex();
		/**
		 *	주어진 메시지에서 정규 패턴과 일치하는 메시지를 얻어오는 메쏘드.
		 *	얻어온 메시지는 반환받은 개체에서 메모리를 해지해 주어야 한다.
		 *	@param 파싱 대상 메시지(문자열)
		 *	@return 파싱된 메시지.
		 */
		char* getMatchedString(char *msg);
		/**
		 *	정규 패턴식을 설정하는 메쏘드.
		 *	@param 정규 패턴식
		 */
		void setPattern(char *pattern);
		/**
		 *	주어진 메시지에 정규 패턴과 일치하는 메시지가 존재하는지 여부를 판단하는 메쏘드.
		 *	@param 메시지(문자열)
		 *	@return true : 정규 패턴과 일치하는 문자열이 존재, false : 정규 패턴과 일치하는 문자열이 없음.
		 */
		bool isMatched(char *str);
		
};

#endif
