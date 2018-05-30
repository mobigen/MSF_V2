#include "CRegex.h"

CRegex::CRegex(char* pattern)
{
	m_pattern = NULL;
	m_pattern = pattern;
	initRegex(&m_re, m_pattern);
}

CRegex::~CRegex()
{
	freeRegex(&m_re);
}

void CRegex::setPattern(char *pattern)
{
	m_pattern = pattern;
	initRegex(&m_re, m_pattern);
}

bool CRegex::isMatched(char* str)
{
	if(getRegMatch(&m_re, str)==NULL){
		return false;
	}else{
		return true;
	}
}

/*  -----------------------------------------------------------------
**  정규 패턴식 초기화 함수. 주어진 pattern으로 regex_t를 초기화(compile)
**  한다. 추후 초기화된 regex_t를 이용하여 패턴 매칭을 하고자 하는 메시지를
**  분석한다.
**  Return value : return 1 if success, else return -1
*/

int CRegex::initRegex(regex_t *re, char *pattern)
{
	int ret=0;
    char buf[1024];

    ret = regcomp(re, pattern, REG_EXTENDED | REG_ICASE);
    if(ret){
        regerror(ret, re, buf, sizeof(buf));
        return -1;
    }

    return 1;
}

/*  ----------------------------------------------------------
**  주어진 메시지를 파싱하여 파싱하고자 하는 정규 패턴 메시를
**  추출하여 추출된 메시지를 반환한다.
**  Return value : return NULL if error occurred, else return parsed message
*/

char *CRegex::getMatchedString(char *msg)
{
	return getMatchedString(&m_re, msg);
}

char* CRegex::getMatchedString(regex_t *re, char *msg)
{
    int ret=0, len=0;
    char *data;
    char buf[1024];
    regmatch_t mat;

    memset(&mat, 0x00, sizeof(mat));
    ret = regexec(re, msg, 1, &mat, 0);
    if(ret){
        regerror(ret, re, buf, sizeof(buf));
        return NULL;
    }

    len = mat.rm_eo - mat.rm_so;
    data = (char *)malloc(len+1);
    if(!data){
        goto ERROR_RETURN;
    }
    memset(data, 0x00, len+1);
    strncpy(data, msg+mat.rm_so, len);

    return data;

ERROR_RETURN:
    if(data) free(data);
    return NULL;
}

/*  -------------------------------------------------------------------
**  주어진 메시지를 파싱하여 파싱하고자 하는 정규 패턴 메시지가 시작되는
**  지점을 가리키는 포인터를 반환한다.
**  Return value : return NULL if error occurred, else return start point
*/

char* CRegex::getMatchedStartPoint(regex_t *re, char *msg)
{
    int ret=0;
    char buf[1024];
    static char *p=NULL;
    regmatch_t mat;

    memset(&mat, 0x00, sizeof(mat));
    ret = regexec(re, msg, 1, &mat, 0);
    if(ret){
        regerror(ret, re, buf, sizeof(buf));
        return NULL;
    }
    p = msg;
    p += mat.rm_so;
    return p;
}

/*  -------------------------------------------------------------------
**  주어진 메시지를 파싱하여 파싱하고자 하는 정규 패턴 메시지가 끝나는
**  지점을 가리키는 포인터를 반환한다.
**  Return value : return NULL if error occurred, else return end point
*/

char* CRegex::getMatchedEndPoint(regex_t *re, char *msg)
{
    int ret=0;
    static char *p=NULL;
    char buf[1024];
    regmatch_t mat;

    memset(&mat, 0x00, sizeof(mat));
    ret = regexec(re, msg, 1, &mat, 0);
    if(ret){
        regerror(ret, re, buf, sizeof(buf));
        return NULL;
    }
    p = msg;
    p += mat.rm_eo;
    return p;
}

/*  -----------------------------------------------------------------
**  주어진 메시지를 파싱하여 정규 표현식에 의해 파싱된 시작점과, 종료점을
**  가리키는 포인터를 가지는 구조체(regmatch_t)를 반환한다.
**  시작포인트(rm_so), 종료포인트(rm_eo).
**  Return value : return NULL if error occurred, else return regmatch_t struct
*/

regmatch_t* CRegex::getRegMatch(regex_t *re, char *msg)
{
    int ret=0;
    static regmatch_t mat;
    char buf[1024];

    memset(&mat, 0x00, sizeof(mat));
    ret = regexec(re, msg, 1, &mat, 0);
    if(ret){
        regerror(ret, re, buf, sizeof(buf));
        return NULL;
    }

    return &mat;
}

void CRegex::freeRegex(regex_t *re)
{
	if(re) regfree(re);
}
