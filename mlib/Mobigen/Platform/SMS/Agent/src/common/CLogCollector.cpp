
// 특정 폴더 밑에 새로운 파일이 생기면, 그 파일의 내용을 하나의 패킷으로
// 만들어서 매니저에게 전달한다.

// 1. 새로 생긴 파일만 전달해야 함. --> 과거의 마지막 전달 시점을 기억해야 함.
//      instance->m_dataQ 속에 저장할 수 있음.

#include "CLogCollector.h"


CLogCollector::CLogCollector()
{
	m_result = NULL;
}

CLogCollector::~CLogCollector()
{
}

void CLogCollector::collect()
{
	makeMessage();
}

void CLogCollector::makeMessage()
{
	int i=0, at=0;
	char buf[1024], temp[32], tab=0x09, *result=NULL, *msg;
	CQueue *instQ = m_pollitem->getInstQ();
	elem *e=NULL;

/*
	for(e=m_pollitem->getItem()->getInstanceQ()->frontNode();
	   e!=NULL; e=m_pollitem->getItem()->getInstanceQ()->getNext(e))
	{
		CItemInstance *instance = (CItemInstance *)e->d;
		CQueue *q = instance->m_dataQ;
		elem *e = q->frontNode();

		char *value = (char*)e->d; // 과거에 저장되어 있는 data임.
    }

*/

/*
    CItemInstance *instance = (CItemInstance *)m_pollitem->getItem()->getInstanceQ()->frontNode()->d;
	CQueue *q = instance->m_dataQ;
	elem *e = q->frontNode();
    char *last_fetched = (char*)e->d; // 과거에 저장되어 있는 data임.
*/

	for(e=instQ->frontNode();e!=NULL;e=instQ->getNext(e)){
		CMessageFormatter msgfmt;
		//
		// <instances>
		//   <instance name="/dir/fullpath">/dir/full/path</instance>
		// <instances>
		// 
		char *dir_fullpath = (char *)e->d; // "dir/fullpath"

		// dir_fullpath에서 새 파일을 뒤진다음 있으면,
		// 패킷 만들고,
		// last_fetched 값을 변경해 두면 됨.

/*
// {

		msgfmt.setItem(m_pollitem->getItem());
		msgfmt.setPollTime(m_pollitem->getPollTime());
		msgfmt.setType(m_pollitem->getPollType());
		if(m_pollitem->getPollType()==TYPE_PASSIVE)
			msgfmt.setCommand((char *)m_pollitem->getCommand().c_str());

		memset(buf, 0x00, sizeof(buf));
		sprintf(buf, "Command%cResult\n", tab);
		msgfmt.setTitle(buf);
		
		if((result=get_popen_result(instname, "r"))!=NULL){
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
// }
*/
	}

	return;
}
