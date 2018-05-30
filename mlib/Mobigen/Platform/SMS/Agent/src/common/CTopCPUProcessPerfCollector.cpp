

#include "CTopCPUProcessPerfCollector.h"


CTopCPUProcessPerfCollector::CTopCPUProcessPerfCollector()
{
	m_list = NULL;
}

CTopCPUProcessPerfCollector::~CTopCPUProcessPerfCollector()
{
	if(m_list!=NULL)
		scCoreViewRelease(&m_list);
}

void CTopCPUProcessPerfCollector::collect()
{
	char *msg=NULL;

	if(m_pollitem->getPollType() == TYPE_EVENT) {
		return;
	}

	m_coreview = m_envvar->getKernelCore()->getCoreView();
	if(	(m_list = scCoreViewPSInfo(m_coreview,SC_SUM_BY_DEFAULT,SC_SORT_BY_PCPU))==NULL ) {
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

void CTopCPUProcessPerfCollector::makeMessage()
{
	int i=0, at=0, topn=-1;
	char buf[1024], temp[32], tab=0x09;
	CQueue *instQ = m_pollitem->getInstQ();
	elem *e=NULL;

	m_msgfmt.setItem(m_pollitem->getItem());
	m_msgfmt.setPollTime(m_pollitem->getPollTime());
	m_msgfmt.setType(m_pollitem->getPollType());
	if(m_pollitem->getPollType()==TYPE_PASSIVE)
		m_msgfmt.setCommand((char *)m_pollitem->getCommand().c_str());

	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "Instance%cCommand%cCpuTime%cCpuUsage\n", tab, tab, tab);
	m_msgfmt.setTitle(buf);

	if(!instQ->isEmpty()){
		char *instname = (char *)instQ->frontNode()->d;
		if(strncmp(instname, "cpu", 3)==0){
			char *p=(char *)strchr(instname, '|');
			if(p){
				p++;
				topn = atoi(p);
			}
		}
	}
	if(m_list!=NULL){
		while((m_psinfo = (scPSInfo *)ll_element_at(m_list, at++))!=NULL){
			if(topn != -1 && at > topn) break;
			memset(buf, 0x00, sizeof(buf));
			sprintf(buf, "%d%c%s%c%02d:%02d:%02d%c%.02f\n",
				m_psinfo->pid, tab,
				m_psinfo->pname, tab,
				m_psinfo->cputime/3600, (m_psinfo->cputime/60)%60,
				m_psinfo->cputime%60, tab,
				m_psinfo->cpuusage);
			m_msgfmt.addMessage(strdup(buf));
		}
	}

	return;
}
