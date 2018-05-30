

#include "CDiskPerfCollector.h"
#include "CAlarmProcessor.h"


CDiskPerfCollector::CDiskPerfCollector()
{
	m_list = NULL;
}

CDiskPerfCollector::~CDiskPerfCollector()
{
	if(m_list!=NULL)
		scCoreViewRelease(&m_list);
}

void CDiskPerfCollector::collect()
{
	char *msg=NULL;

	m_coreview = m_envvar->getKernelCore()->getCoreView();
	if(	(m_list = scCoreViewFSInfo(m_coreview))==NULL ) {
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
		if(m_pollitem->getPollType() == TYPE_PASSIVE) {
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

void CDiskPerfCollector::makeMessage()
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
	sprintf(buf, "Instance%cTOTAL_SIZE(KB)%cUSED_SIZE(KB)%cUSAGE(%%)\n",
		tab, tab, tab);
	m_msgfmt.setTitle(buf);

	if(m_list!=NULL){
		while((m_fsinfo = (scFSInfo *)ll_element_at(m_list, at++))!=NULL){
			if(!instQ->isEmpty()){
				for(e=instQ->frontNode();e!=NULL;e=instQ->getNext(e)){
					char *instname = (char *)e->d;
					if(strcmp(instname, m_fsinfo->mntpoint)==0){
						memset(buf, 0x00, sizeof(buf));
						sprintf(buf, "%s%c%lu%c%lu%c%.02f\n",
							m_fsinfo->mntpoint, tab,
							m_fsinfo->sizetotal, tab, 
							m_fsinfo->sizeused, tab, m_fsinfo->sizeusage);
						m_msgfmt.addMessage(strdup(buf));
					}
				}
			}else{
				memset(buf, 0x00, sizeof(buf));
				sprintf(buf, "%s%c%lu%c%lu%c%.02f\n",
					m_fsinfo->mntpoint, tab,
					m_fsinfo->sizetotal, tab, 
					m_fsinfo->sizeused, tab, m_fsinfo->sizeusage);
				m_msgfmt.addMessage(strdup(buf));
			}
		}
	}

	return;
}


void CDiskPerfCollector::isOverThreshold(CItemCondition *cond)
{
	int at=0,i=0;
	char temp[32];
	bool b=false;

	if(cond->getElement() > 3) return;
	if (m_list == NULL) return;

	while((m_fsinfo = (scFSInfo *)ll_element_at(m_list, at++))!=NULL) {
		if(cond->getInstanceName() == "ALL" || cond->getInstanceName() ==  m_fsinfo->mntpoint) {
			/* check alarm */
			if(cond->getElement() == 1) { /* total */
				b = cond->isOverThreshold(m_fsinfo->sizetotal);
			} else if(cond->getElement() == 2) { /* used */
				b = cond->isOverThreshold(m_fsinfo->sizeused);
			} else if(cond->getElement() == 3) { /* usage */
				b = cond->isOverThreshold(m_fsinfo->sizeusage);
			}
			checkAlarm(cond, m_fsinfo->mntpoint, b, m_fsinfo);
		}
	}

	return ;
}

void CDiskPerfCollector::checkAlarm(CItemCondition *_cond, char *inst, bool ialarm, scFSInfo *fs_info)
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

	sprintf(buf, "Instance%cTOTAL_SIZE(KB)%cUSED_SIZE(KB)%cUSAGE(%%)\n",
		tab, tab, tab);
	msgfmt.setTitle(buf);

	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "%s%c%lu%c%lu%c%.02f\n",
		fs_info->mntpoint, tab,
		fs_info->sizetotal, tab, 
		fs_info->sizeused, tab, fs_info->sizeusage);

	msgfmt.addMessage(strdup(buf));

	msg = msgfmt.makeMessage();
	m_envvar->getEventQ()->enqueue(msg, NULL);		

	return;
}
