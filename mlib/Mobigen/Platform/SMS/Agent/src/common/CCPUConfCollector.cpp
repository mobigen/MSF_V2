

#include "CCPUConfCollector.h"


CCPUConfCollector::CCPUConfCollector()
{
}

CCPUConfCollector::~CCPUConfCollector()
{
}

void CCPUConfCollector::collect()
{
	char *msg=NULL;

	if(m_pollitem->getPollType() == TYPE_EVENT) {
		return;
	}

	m_coreview = m_envvar->getKernelCore()->getCoreView();
	if(	scCoreViewBasicInfo(m_coreview, &m_sysinfo)==SC_ERR //||
		//scCoreViewCpuStatus(m_coreview, &m_ucpu, m_mcpu, &m_ncpu) == SC_ERR 
		) 
	{
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

void CCPUConfCollector::makeMessage()
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
	sprintf(buf, "INSTANCE%cMHz\n", tab);
	m_msgfmt.setTitle(buf);

	for(i=0;i<m_sysinfo.ncpu;i++)
	{
		memset(temp, 0x00, sizeof(temp));
		sprintf(temp, "cpu%d", i);
		if(!instQ->isEmpty()){
			for(e=instQ->frontNode();e!=NULL;e=instQ->getNext(e)){
				char *instname = (char *)e->d;
				if(strcmp(instname, temp)==0){
					memset(buf, 0x00, sizeof(buf));
					sprintf(buf, "%s%c%d\n", temp, tab, m_sysinfo.clockspeed);
					m_msgfmt.addMessage(strdup(buf));
				}
			}
		}else{
			memset(buf, 0x00, sizeof(buf));
			sprintf(buf, "%s%c%d\n", temp, tab, m_sysinfo.clockspeed);
			m_msgfmt.addMessage(strdup(buf));
		}
	}

	return;
}
