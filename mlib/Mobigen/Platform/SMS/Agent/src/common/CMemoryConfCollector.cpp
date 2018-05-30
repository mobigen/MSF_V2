

#include "CMemoryConfCollector.h"


CMemoryConfCollector::CMemoryConfCollector()
{
}

CMemoryConfCollector::~CMemoryConfCollector()
{
}

void CMemoryConfCollector::collect()
{
	char *msg=NULL;

	if(m_pollitem->getPollType() == TYPE_EVENT) {
		return;
	}

	m_coreview = m_envvar->getKernelCore()->getCoreView();
	if(	scCoreViewMemStatus(m_coreview, &m_mem)==SC_ERR ) {
		m_envvar->getKernelCore()->returnCoreView(m_coreview);
		return;
	}
	m_envvar->getKernelCore()->returnCoreView(m_coreview);

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

void CMemoryConfCollector::makeMessage()
{
	int i=0;
	char buf[1024], temp[32], tab=0x09;
	CQueue *instQ = m_pollitem->getInstQ();
	elem *e=NULL;

	m_msgfmt.setItem(m_pollitem->getItem());
	m_msgfmt.setPollTime(m_pollitem->getPollTime());
	m_msgfmt.setType(m_pollitem->getPollType());
	if(m_pollitem->getPollType()==TYPE_PASSIVE)
		m_msgfmt.setCommand((char *)m_pollitem->getCommand().c_str());

	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "MemorySize(KB)%cSwapSize(KB)\n", tab);
	m_msgfmt.setTitle(buf);

	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "%lu%c%lu\n", m_mem.m_total, tab, m_mem.s_total);
	m_msgfmt.addMessage(strdup(buf));

	return;
}
