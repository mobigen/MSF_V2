

#include "CCPULoadPerfCollector.h"
#include "CAlarmProcessor.h"


CCPULoadPerfCollector::CCPULoadPerfCollector()
{
}

CCPULoadPerfCollector::~CCPULoadPerfCollector()
{
}

void CCPULoadPerfCollector::collect()
{
	char *msg=NULL;

	m_coreview = m_envvar->getKernelCore()->getCoreView();
	if(	scCoreViewVMStatus(m_coreview, &m_vmstat)==SC_ERR ) {
		m_envvar->getKernelCore()->returnCoreView(m_coreview);
		return;
	}
	m_envvar->getKernelCore()->returnCoreView(m_coreview);


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

void CCPULoadPerfCollector::makeMessage()
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
	sprintf(buf, "QUEUE1%cQUEUE5%cQUEUE15\n", tab, tab);
	m_msgfmt.setTitle(buf);

	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "%.02f%c%.02f%c%.02f\n", m_vmstat.la_1min, tab,
		m_vmstat.la_5min, tab, m_vmstat.la_15min);
	m_msgfmt.addMessage(strdup(buf));

	return;
}

void CCPULoadPerfCollector::isOverThreshold(CItemCondition *cond)
{
	int at=0,i=0;
	char temp[32];
	bool b=false;

	if(cond->getElement() > 2) return;

	memset(temp, 0x00, sizeof(temp));

	/* check alarm */
	if(cond->getElement() == 0) { /* QUEUE1 */
		b = cond->isOverThreshold( m_vmstat.la_1min );
		strcpy(temp, "QUEUE1");
	} else if(cond->getElement() == 1) { /* QUEUE5 */
		b = cond->isOverThreshold( m_vmstat.la_5min );
		strcpy(temp, "QUEUE5");
	} else if(cond->getElement() == 2) { /* QUEUE15 */
		b = cond->isOverThreshold( m_vmstat.la_15min );
		strcpy(temp, "QUEUE15");
	} 
	checkAlarm(cond, temp, b);

	return ;
}


void CCPULoadPerfCollector::checkAlarm(CItemCondition *_cond, char *inst, bool ialarm)
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
	sprintf(buf, "Instance%cQUEUE1%cQUEUE5%cQUEUE15\n", tab, tab, tab);
	msgfmt.setTitle(buf);

	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "%s%c%.02f%c%.02f%c%.02f\n", inst, tab, m_vmstat.la_1min, tab,
		m_vmstat.la_5min, tab, m_vmstat.la_15min);
	msgfmt.addMessage(strdup(buf));

	msg = msgfmt.makeMessage();
	m_envvar->getEventQ()->enqueue(msg, NULL);		

	return;
}