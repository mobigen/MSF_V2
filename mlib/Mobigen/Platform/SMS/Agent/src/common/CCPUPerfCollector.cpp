

#include "CCPUPerfCollector.h"
#include "CAlarmProcessor.h"


CCPUPerfCollector::CCPUPerfCollector()
{
}

CCPUPerfCollector::~CCPUPerfCollector()
{
}

void CCPUPerfCollector::collect()
{
	char *msg=NULL;
	time_t tt;

	time(&tt);
	if((tt - g_cputime) >= 1){
		m_coreview = m_envvar->getKernelCore()->getCoreView();
		if(scCoreViewCpuStatus(m_coreview, &m_ucpu, m_mcpu, &m_ncpu)==SC_ERR) {
			m_envvar->getKernelCore()->returnCoreView(m_coreview);
			return;
		}
		g_cputime = tt;
		memcpy(&g_ucpu, &m_ucpu, sizeof(scCpuStatus));
		memcpy(&g_mcpu, &m_mcpu, SC_MAX_CPU_NUM * sizeof(scCpuStatus));
		g_ncpu = m_ncpu;
		m_envvar->getKernelCore()->returnCoreView(m_coreview);
	}else {
		m_coreview = m_envvar->getKernelCore()->getCoreView();
		memcpy(&m_ucpu, &g_ucpu, sizeof(scCpuStatus));
		memcpy(&m_mcpu, &g_mcpu, SC_MAX_CPU_NUM * sizeof(scCpuStatus));
		m_ncpu = g_ncpu;
		m_envvar->getKernelCore()->returnCoreView(m_coreview);
	}

	if(m_pollitem->getPollType() == TYPE_EVENT){
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

void CCPUPerfCollector::makeMessage()
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
	sprintf(buf, "INSTANCE%cUSER(%%)%cKERNEL(%%)%cCPU(%%)%cWAIT(%%)%cIDLE(%%)\n",
		tab, tab, tab, tab, tab);
	m_msgfmt.setTitle(buf);

	for(i=0;i<m_ncpu;i++)
	{
		memset(temp, 0x00, sizeof(temp));
		sprintf(temp, "cpu%d", m_mcpu[i].id);
		if(!instQ->isEmpty()){
			for(e=instQ->frontNode();e!=NULL;e=instQ->getNext(e)){
				char *instname = (char *)e->d;
				if(strcmp(instname, temp)==0){
					memset(buf, 0x00, sizeof(buf));
					sprintf(buf, "%s%c%.02f%c%.02f%c%.02f%c%.02f%c%.02f\n",
						temp, tab, m_mcpu[i].user, tab, m_mcpu[i].system,
						tab, m_mcpu[i].user + m_mcpu[i].system,
						tab, m_mcpu[i].etc, tab, m_mcpu[i].idle);
					m_msgfmt.addMessage(strdup(buf));
				}
			}
		}else{
			memset(buf, 0x00, sizeof(buf));
			sprintf(buf, "%s%c%.02f%c%.02f%c%.02f%c%.02f%c%.02f\n",
				temp, tab, m_mcpu[i].user, tab, m_mcpu[i].system,
				tab, m_mcpu[i].user + m_mcpu[i].system,
				tab, m_mcpu[i].etc, tab, m_mcpu[i].idle);
			m_msgfmt.addMessage(strdup(buf));
		}

	}
	
	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "%s%c%.02f%c%.02f%c%.02f%c%.02f%c%.02f\n",
		"total", tab, m_ucpu.user, tab, m_ucpu.system,
		tab, m_ucpu.user + m_ucpu.system,
		tab, m_ucpu.etc, tab, m_ucpu.idle);
	m_msgfmt.addMessage(strdup(buf));

	return;
}

void CCPUPerfCollector::isOverThreshold(CItemCondition *cond)
{
	int at=0,i=0;
	char temp[32];
	bool b=false;

	if(cond->getElement() > 5) return;

	for(i=0;i<m_ncpu;i++)
	{
		memset(temp, 0x00, sizeof(temp));
		sprintf(temp, "cpu%d", m_mcpu[i].id);

		if(cond->getInstanceName() == "ALL" || cond->getInstanceName() == temp){
			/* check alarm */
			if(cond->getElement() == 1){ /* user */
				b = cond->isOverThreshold(m_mcpu[i].user);
			}else if(cond->getElement() == 2) { /* system */
				b = cond->isOverThreshold(m_mcpu[i].system);
			}else if(cond->getElement() == 3) { /* cpu */
				b = cond->isOverThreshold(m_mcpu[i].user + m_mcpu[i].system);
			}else if(cond->getElement() == 4) { /* wait */
				b = cond->isOverThreshold(m_mcpu[i].etc);
			}else if(cond->getElement() == 5) { /* idle */
				b = cond->isOverThreshold(m_mcpu[i].idle);
			}
			checkAlarm(cond, temp, b, &m_mcpu[i]);
		}
	}

	if(cond->getInstanceName() == "ALL" || cond->getInstanceName() == "total"){
		/* check alarm */
		if(cond->getElement() == 1){ /* user */
			b = cond->isOverThreshold(m_ucpu.user);
		}else if(cond->getElement() == 2) { /* system */
			b = cond->isOverThreshold(m_ucpu.system);
		}else if(cond->getElement() == 3) { /* cpu */
			b = cond->isOverThreshold(m_ucpu.user + m_ucpu.system);
		}else if(cond->getElement() == 4) { /* wait */
			b = cond->isOverThreshold(m_ucpu.etc);
		}else if(cond->getElement() == 5) { /* idle */
			b = cond->isOverThreshold(m_ucpu.idle);
		}
		checkAlarm(cond, "total", b, &m_ucpu);
	}

	return ;
}

void CCPUPerfCollector::checkAlarm(CItemCondition *_cond, char *inst, bool ialarm, scCpuStatus *cpu)
{
	st_item_alarm alarm;
	bool _ialarm = false;
	CItem *item = this->getPolicyItem()->getItem();
	CMessageFormatter msgfmt;
	char buf[1024], tab=0x09, *msg;

	memset(&alarm, 0x00, sizeof(st_item_alarm));
	strncpy(alarm.instance, inst, sizeof(alarm.instance));
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
	sprintf(buf,
		"INSTANCE%cUSER(%%)%cKERNEL(%%)%cCPU(%%)%cWAIT(%%)%cIDLE(%%)\n",
		tab, tab, tab, tab, tab);
	msgfmt.setTitle(buf);

	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "%s%c%.02f%c%.02f%c%.02f%c%.02f%c%.02f\n",
		inst, tab, cpu->user, tab, cpu->system,
		tab, cpu->user + cpu->system,
		tab, cpu->etc, tab, cpu->idle);
	msgfmt.addMessage(strdup(buf));

	msg = msgfmt.makeMessage();
	m_envvar->getEventQ()->enqueue(msg, NULL);		

	return;
}
