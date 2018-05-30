

#include "CShellCommandCollector.h"


CShellCommandCollector::CShellCommandCollector()
{
	m_result = NULL;
}

CShellCommandCollector::~CShellCommandCollector()
{
}

void CShellCommandCollector::collect()
{
	makeMessage();
}

void CShellCommandCollector::makeMessage()
{
	int i=0, at=0;
	char buf[1024], temp[32], tab=0x09, *result=NULL, *msg;
	CQueue *instQ = m_pollitem->getInstQ();
	elem *e=NULL;
	for(e=instQ->frontNode();e!=NULL;e=instQ->getNext(e)){
		CMessageFormatter msgfmt;
		//
		// <instances>
		//   <instance name="명령어">명령어</instance>
		// <instances>
		// 
		char *instname = (char *)e->d;


		msgfmt.setItem(m_pollitem->getItem());
		msgfmt.setPollTime(m_pollitem->getPollTime());
		msgfmt.setType(m_pollitem->getPollType());
		if(m_pollitem->getPollType()==TYPE_PASSIVE)
			msgfmt.setCommand((char *)m_pollitem->getCommand().c_str());

		memset(buf, 0x00, sizeof(buf));
		sprintf(buf, "Command%cResult\n", tab);
		msgfmt.setTitle(buf);
		
		if((result=get_popen_result(instname, "r"))!=NULL) {
			int len = strlen(result)+128;
			char *data = (char *)malloc(len);
			memset(data, 0x00, len);
			sprintf(data, "%s%c%s\n", instname, tab, result);
			msgfmt.addMessage(data);
			msg = msgfmt.makeMessage();

			if(m_pollitem->getPollType() == TYPE_PASSIVE){
				m_envvar->getRespQ()->enqueue(msg, NULL);		
			}else{
				if(isShortPerf()==true){
					m_envvar->getShortPerfQ()->enqueue(msg, NULL);		
				}else{
					m_envvar->getLongPerfQ()->enqueue(msg, NULL);		
				}
			}

			free(result);
		}
	}

	return;
}
