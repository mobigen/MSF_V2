

#include "CProcessHealthCollector.h"
#include "CAlarmProcessor.h"


CProcessHealthCollector::CProcessHealthCollector()
{
	m_list = NULL;
	m_procQ = new CQueue();
}

CProcessHealthCollector::~CProcessHealthCollector()
{
	if(m_list!=NULL)
		scCoreViewRelease(&m_list);
	if(m_procQ!=NULL)
		delete m_procQ;
}

void CProcessHealthCollector::collect()
{
	char *msg=NULL;

	m_coreview = m_envvar->getKernelCore()->getCoreView();
	if(	(m_list = scCoreViewPSInfo(m_coreview,SC_SUM_BY_DEFAULT,SC_SORT_BY_DEFAULT))==NULL ) {
		m_envvar->getKernelCore()->returnCoreView(m_coreview);
		return;
	}
	m_envvar->getKernelCore()->returnCoreView(m_coreview);

	initInstance();

	if(m_pollitem->getPollType() != TYPE_EVENT){
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
	}else{
		CAlarmProcessor ap(this);
		ap.check();
	}
}

void CProcessHealthCollector::initInstance()
{
	int at=0;
	CQueue *instQ = m_pollitem->getInstQ();
	elem *e=NULL;

	for(e=instQ->frontNode();e!=NULL;e=instQ->getNext(e)){
		char *instname = (char *)e->d;
		scPSInfo *_psinfo = (scPSInfo *)malloc(sizeof(scPSInfo));
		memset(_psinfo, 0x00, sizeof(scPSInfo));
		strcpy(_psinfo->args, instname);
		m_procQ->enqueue(_psinfo, NULL);
	}

	if(m_list!=NULL){
		while((m_psinfo = (scPSInfo *)ll_element_at(m_list, at++))!=NULL){
			for(e=m_procQ->frontNode();e!=NULL;e=m_procQ->getNext(e)){
				scPSInfo *_psinfo = (scPSInfo *)e->d;

				if(strcmp(_psinfo->args, m_psinfo->args)==0) {
					_psinfo->pcount++;
				}
			}
		}
	}
}

void CProcessHealthCollector::makeMessage()
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
	sprintf(buf, "Command%c | %cCOUNT\n", tab, tab);
	m_msgfmt.setTitle(buf);

	for(e=m_procQ->frontNode();e!=NULL;e=m_procQ->getNext(e)){
		scPSInfo *_psinfo = (scPSInfo *)e->d;
		memset(buf, 0x00, sizeof(buf));
		sprintf(buf, "%s%c | %c%d\n", _psinfo->pname, tab, tab, _psinfo->pcount);
		m_msgfmt.addMessage(strdup(buf));
	}

	return;
}

void CProcessHealthCollector::isOverThreshold(CItemCondition *cond)
{
	bool b=false;
	char temp[256];
	elem *e=NULL;
	bool isChkProcess=false; //condition이 0인경우에 처리하는 플래그
	for(e=m_procQ->frontNode();e!=NULL;e=m_procQ->getNext(e)) {
		scPSInfo *_psinfo = (scPSInfo *)e->d;

		if(cond->getInstanceName() == "ALL" || 
				cond->getInstanceName() == _psinfo->args)
		{
			b = cond->isOverThreshold(_psinfo->pcount);
			checkAlarm(cond, _psinfo, b);
			isChkProcess = true;
		}
	}


	if (isChkProcess == false && cond->getCondition() == "==0") {
		scPSInfo psinfo;
		strncpy(psinfo.args, cond->getInstanceName().c_str(),
			sizeof(psinfo.args));
		psinfo.pcount = 0;
		checkAlarm(cond, &psinfo, true);
	}
}

void CProcessHealthCollector::checkAlarm(CItemCondition *cond, scPSInfo *psinfo, bool ialarm)
{
	st_item_alarm alarm;
	bool _ialarm = false;
	CItem *item = this->getPolicyItem()->getItem();
	CMessageFormatter msgfmt;
	char buf[1024], tab=0x09, *msg;

	memset(&alarm, 0x00, sizeof(st_item_alarm));
	strcpy(alarm.instance, psinfo->pname);
	alarm.condid = cond->getIndex();

	_ialarm = item->isAlarm(&alarm);

	if(ialarm == false && _ialarm == false) return;
	else if(ialarm == true && _ialarm == true) return;
	else if(ialarm == true && _ialarm == false) /* alarm occurred */
	{
		st_item_alarm *ia = (st_item_alarm *)malloc(sizeof(st_item_alarm));
		ia->condid = alarm.condid;
		strcpy(ia->instance, alarm.instance);
		item->addAlarm(ia);
	} else if(ialarm == false && _ialarm == true) /* alarm cleared */
	{
		item->delAlarm(&alarm);
	}

	msgfmt.setItem(m_pollitem->getItem());
	msgfmt.setPollTime(m_pollitem->getPollTime());
	msgfmt.setType(m_pollitem->getPollType());
	msgfmt.setItemCondition(cond);
	msgfmt.setEventStatus(ialarm);

	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "Command%c | %cCOUNT\n", tab, tab);
	msgfmt.setTitle(buf);

	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "%s%c%d\n", psinfo->args, tab, psinfo->pcount);
	msgfmt.addMessage(strdup(buf));

	msg = msgfmt.makeMessage();
	m_envvar->getEventQ()->enqueue(msg, NULL);

	return;
}
