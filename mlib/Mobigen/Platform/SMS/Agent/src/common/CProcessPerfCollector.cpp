

#include "CProcessPerfCollector.h"
#include "CAlarmProcessor.h"


CProcessPerfCollector::CProcessPerfCollector()
{
	m_list = NULL;
}

CProcessPerfCollector::~CProcessPerfCollector()
{
	if(m_list!=NULL)
		scCoreViewRelease(&m_list);
}

void CProcessPerfCollector::collect()
{
	char *msg=NULL;

	m_coreview = m_envvar->getKernelCore()->getCoreView();
	if(	(m_list = scCoreViewPSInfo(m_coreview,SC_SUM_BY_DEFAULT,SC_SORT_BY_PCPU))==NULL ) {
		m_envvar->getKernelCore()->returnCoreView(m_coreview);
		return;
	}
	m_envvar->getKernelCore()->returnCoreView(m_coreview);



	if(m_pollitem->getPollType() == TYPE_EVENT) {
		CAlarmProcessor ap(this);
		ap.check();
	} else {
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
}

void CProcessPerfCollector::makeMessage()
{
	int i=0, at=0;
	char buf[2048], temp[32], tab=0x09;
	CQueue *instQ = m_pollitem->getInstQ();
	elem *e=NULL;

	m_msgfmt.setItem(m_pollitem->getItem());
	m_msgfmt.setPollTime(m_pollitem->getPollTime());
	m_msgfmt.setType(m_pollitem->getPollType());
	if(m_pollitem->getPollType()==TYPE_PASSIVE)
		m_msgfmt.setCommand((char *)m_pollitem->getCommand().c_str());

	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "Command%c | %cPID%cPPID%c | %cCpuUsed%cMemoryUsed\n", tab, tab, tab, tab, tab, tab);
	m_msgfmt.setTitle(buf);

	if(m_list!=NULL){
		while((m_psinfo = (scPSInfo *)ll_element_at(m_list, at++))!=NULL){
			if(!instQ->isEmpty()){
				for(e=instQ->frontNode();e!=NULL;e=instQ->getNext(e)){
					char *instname = (char *)e->d;
					if(strcmp(instname, m_psinfo->pname)==0){
						memset(buf, 0x00, sizeof(buf));
						sprintf(buf, "%s%c%s%c | %c%d%c%d%c | %c%.02f%c%.02f\n",
							m_psinfo->pname, tab, m_psinfo->args, tab,
							tab, m_psinfo->pid, tab, m_psinfo->ppid, tab,	
							tab, m_psinfo->cpuusage, tab, m_psinfo->memusage);
						m_msgfmt.addMessage(strdup(buf));
					}
				}
			}
			else{
				memset(buf, 0x00, sizeof(buf));
				sprintf(buf, "%s%c%s%c | %c%d%c%d%c | %c%.02f%c%.02f\n",
					m_psinfo->pname, tab, m_psinfo->args, tab,
					tab, m_psinfo->pid, tab, m_psinfo->ppid, tab,
					tab, m_psinfo->cpuusage, tab, m_psinfo->memusage);
				m_msgfmt.addMessage(strdup(buf));
			}
		}
	}

	return;
}


void CProcessPerfCollector::isOverThreshold(CItemCondition *cond)
{
	int at=0,i=0;
	char temp[250];
	bool b=false;

	if(cond->getElement() > 2) return;
	if (m_list == NULL) return;

	while((m_psinfo = (scPSInfo *)ll_element_at(m_list, at++))!=NULL) {

		if(cond->getInstanceName() == "ALL" || cond->getInstanceName() ==  m_psinfo->args) {
			/* check alarm */
			if(cond->getElement() == 1) { /* cpuusage */
				b = cond->isOverThreshold( m_psinfo->cpuusage );
			} else if(cond->getElement() == 2) { /* memusage */
				b = cond->isOverThreshold( m_psinfo->memusage );
			} 
			checkAlarm(cond, temp, b, m_psinfo);
		}
	}

	return ;
}

void CProcessPerfCollector::checkAlarm(CItemCondition *_cond, char *inst, bool ialarm, scPSInfo *psinfo)
{
	st_item_alarm alarm;
	bool _ialarm = false;
	CItem *item = this->getPolicyItem()->getItem();
	CMessageFormatter msgfmt;
	char buf[1024], tab=0x09, *msg;

	memset(&alarm, 0x00, sizeof(st_item_alarm));
	strncpy(alarm.instance, inst, sizeof(alarm.instance)-1);
	alarm.condid = _cond->getIndex();

	_ialarm = item->isAlarm(&alarm);

	if(ialarm == false && _ialarm == false) return;
	else if(ialarm == true && _ialarm == true) return;
	else if(ialarm == true && _ialarm == false){ /* alarm occurred */
		st_item_alarm *ia = (st_item_alarm *)malloc(sizeof(st_item_alarm));
		memset(ia, 0x00, sizeof(st_item_alarm));
		ia->condid = alarm.condid;
		strcpy(ia->instance, alarm.instance);
		item->addAlarm(ia);
	}else if(ialarm == false && _ialarm == true){ /* alarm cleared */
		item->delAlarm(&alarm);
	}

	msgfmt.setItem(m_pollitem->getItem());
	msgfmt.setPollTime(m_pollitem->getPollTime());
	msgfmt.setType(m_pollitem->getPollType());
	msgfmt.setItemCondition(_cond);
	msgfmt.setEventStatus(ialarm);

	memset(buf, 0x00, sizeof(buf));

	sprintf(buf, "Command%c | %cPID%cPPID%c | %cCpuUsed%cMemoryUsed\n", tab, tab, tab, tab, tab, tab);
	msgfmt.setTitle(buf);

	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "%s%c%s%c | %c%d%c%d%c | %c%.02f%c%.02f\n",
		psinfo->pname, tab, psinfo->args, tab,
		tab, psinfo->pid, tab, psinfo->ppid, tab,	
		tab, psinfo->cpuusage, tab, psinfo->memusage);

	msgfmt.addMessage(strdup(buf));

	msg = msgfmt.makeMessage();
	m_envvar->getEventQ()->enqueue(msg, NULL);		

	return;
}
