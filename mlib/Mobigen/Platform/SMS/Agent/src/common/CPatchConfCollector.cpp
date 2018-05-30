

#include "CPatchConfCollector.h"


CPatchConfCollector::CPatchConfCollector()
{
	m_list = NULL;
}

CPatchConfCollector::~CPatchConfCollector()
{
	if(m_list!=NULL)
		scCoreViewRelease(&m_list);
}

void CPatchConfCollector::collect()
{
	char *msg=NULL;

	if(m_pollitem->getPollType() == TYPE_EVENT) {
		return;
	}

	m_coreview = m_envvar->getKernelCore()->getCoreView();
	m_list = scCoreViewSysPatchInfo(m_coreview);
	m_envvar->getKernelCore()->returnCoreView(m_coreview);

	if(	m_list == NULL ) {
		return;
	}

	makeMessage();
	msg = m_msgfmt.makeMessage();

	if(m_pollitem->getPollType() == TYPE_PASSIVE){
		m_envvar->getRespQ()->enqueue(msg, NULL);		
	}else{
		if(isShortPerf()==true){
			m_envvar->getShortPerfQ()->enqueue(msg, NULL);		
		}else{
			m_envvar->getLongPerfQ()->enqueue(msg, NULL);		
		}
	}
}

void CPatchConfCollector::makeMessage()
{
	int i=0, at=0;
	char buf[1024], temp[32], tab=0x09;
	CQueue *instQ = m_pollitem->getInstQ();
	elem *e=NULL;

	m_msgfmt.setItem(m_pollitem->getItem());
	m_msgfmt.setPollTime(m_pollitem->getPollTime());
	m_msgfmt.setType(m_pollitem->getPollType());
	if(m_pollitem->getPollType()==TYPE_PASSIVE)
		m_msgfmt.setCommand((char *)m_pollitem->getCommand().c_str());

	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "Index%cpatchname\n", tab);
	m_msgfmt.setTitle(buf);

	if(m_list!=NULL){
		while((m_patch = (scSysPatchInfo *)ll_element_at(m_list, at++))!=NULL){
			if(!instQ->isEmpty()){
				for(e=instQ->frontNode();e!=NULL;e=instQ->getNext(e)){
					char *instname = (char *)e->d;
					if(strcmp(instname, m_patch->name)==0){
						memset(buf, 0x00, sizeof(buf));
						sprintf(buf, "patch%d%c%s\n", at, tab, m_patch->name);
						m_msgfmt.addMessage(strdup(buf));
					}
				}
			}else{
				memset(buf, 0x00, sizeof(buf));
				sprintf(buf, "patch%d%c%s\n", at, tab, m_patch->name);
				m_msgfmt.addMessage(strdup(buf));
			}
		}
	}

	return;
}
