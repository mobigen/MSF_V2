
#include "CMessageFormatter.h"


CMessageFormatter::CMessageFormatter()
{
	m_item = NULL;
	m_cond = NULL;
	m_type = TYPE_ACTIVE;
	m_cmd = "";
	m_code = "";
	m_title = "";
	m_cond = NULL;
}

CMessageFormatter::~CMessageFormatter()
{
}

char * CMessageFormatter::makeMessage()
{
	unsigned long mlen=0, len=0;
	char *msg=NULL, *s=NULL;
	char buf[1024];
	elem *e=NULL;

	char hname[128], timestr[32];
	time_t curtime;
	struct tm *ptm=NULL;

	if(m_item == NULL) m_code  = "UNKNOWN_CODE";
	else m_code = m_item->getCode();

	memset(buf, 0x00, sizeof(buf));
	memset(hname, 0x00, sizeof(hname));
	memset(timestr, 0x00, sizeof(timestr));
	gethostname(hname, sizeof(hname)-1);

	time(&curtime);
	ptm = localtime(&m_polltime);
	strftime(timestr, sizeof(timestr)-1, "%Y-%m-%d %H:%M:%S", ptm);

	if(m_type==TYPE_PASSIVE){
		sprintf(buf, "%s	%s\n"
					 "%s	%s\n"
					 "PASSIVE	%s\n"
					 "%s", 
					 hname, timestr, m_code.c_str(),
					 m_item==NULL ? "No Description" : m_item->getName().c_str(),
					 m_cmd=="" ? "UNKNOWN_COMMAND" : m_cmd.c_str(),
					 m_title.c_str() );

	}else if(m_type==TYPE_ACTIVE){

		sprintf(buf, "%s	%s\n"
					 "%s	%s\n"
					 "ACTIVE\n"
					 "%s", hname, timestr, m_code.c_str(), m_item->getName().c_str(),
					 m_title.c_str() );

	}else if(m_type==TYPE_EVENT){

		sprintf(buf, "%s	%s\n"
					 "%s	%s\n"
					 "EVENT	%s	%d	%s	%s\n"
					 "%s", 
					 hname, timestr, m_code.c_str(), 
					 m_item==NULL ? "No Description" : m_item->getName().c_str(),
					 m_cond == NULL ? "N/A" : m_cond->getCondition().c_str(),
					 m_cond == NULL ? 0 : m_cond->getElement(),
					 m_cond == NULL ? "N/A" : m_cond->getSeverity().c_str(),
					 m_alarm == true ? "START" : "END",
					 m_title.c_str() );

	}

	mlen = strlen(buf)+1;
	len = strlen(buf);
	msg = (char *)malloc(mlen);
	memset(msg, 0x00, mlen);
	strcpy(msg, buf);

	for(e=m_msgQ.frontNode(); e!=NULL; e=m_msgQ.getNext(e)){
		s = (char *)e->d;
		mlen += strlen(s);
		msg = (char *)realloc(msg, mlen);
		strncpy(msg+len, s, strlen(s));
		len+=strlen(s);
	}
	
	memset(buf, 0x00, sizeof(buf));
	strcpy(buf, "COMPLETED\n\n");
	mlen += strlen(buf);
	msg = (char *)realloc(msg, mlen);
	strncpy(msg+len, buf, strlen(buf));
	msg[mlen-1] = 0x00;
	return msg;
}

std::string CMessageFormatter::makeErrorMessage(std::string err_str)
{
	return makeErrorMessage(err_str.c_str());
}

std::string CMessageFormatter::makeErrorMessage(char *errmsg)
{
	char msg[1024], hname[128], timestr[32];
	time_t curtime;
	struct tm *ptm=NULL;
	std::string str;

	if(m_item == NULL) m_code  = "UNKNOWN_CODE";
	else m_code = m_item->getCode();

	memset(msg, 0x00, sizeof(msg));
	memset(hname, 0x00, sizeof(hname));
	memset(timestr, 0x00, sizeof(timestr));
	gethostname(hname, sizeof(hname)-1);

	time(&curtime);
	ptm = localtime(&curtime);
	strftime(timestr, sizeof(timestr)-1, "%Y-%m-%d %H:%M:%S", ptm);

	sprintf(msg, "%s %s\n"
				 "%s\n"
				 "%s\n"
				 "%s\n"
				 "COMPLETED\n\n", hname, timestr, m_code.c_str(), getTypeCode().c_str(), errmsg);
	str = msg;
	return str;
}

void CMessageFormatter::setItemCode(char *code)
{
	m_code = code;
}

void CMessageFormatter::setItemCode(std::string strcode)
{
	m_code = strcode;
}

void CMessageFormatter::setItemCondition(CItemCondition *cond)
{
	m_cond = cond;
}

std::string CMessageFormatter::getTypeCode()
{
	std::string typecode = "";

	if(m_type == TYPE_PASSIVE) typecode = "PASSIVE";
	else if(m_type == TYPE_EVENT) typecode = "EVENT";
	else typecode = "ACTIVE";

	return typecode;
}
