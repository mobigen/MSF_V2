

#include "CIFPerfCollector.h"
#include "CAlarmProcessor.h"


CIFPerfCollector::CIFPerfCollector()
{
	m_list = NULL;
}

CIFPerfCollector::~CIFPerfCollector()
{
	if(m_list!=NULL)
		scCoreViewRelease(&m_list);
}

void CIFPerfCollector::collect()
{
	char *msg=NULL;

	m_coreview = m_envvar->getKernelCore()->getCoreView();
	if(	(m_list = scCoreViewInterfaceStatus(m_coreview))==NULL ) {
		m_envvar->getKernelCore()->returnCoreView(m_coreview);
		return;
	}
	m_envvar->getKernelCore()->returnCoreView(m_coreview);

	if(m_pollitem->getPollType() == TYPE_EVENT){
		CAlarmProcessor ap(this);
		ap.check();
	}else{
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

void CIFPerfCollector::makeMessage()
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
	sprintf(buf, "Instance%cPacketIn%cPacketOut%cPacketInError%cPacketOutError%cCollision%cOctIn%cOctOut%cOctInUsage(%)%cOctOutUsage(%)\n", 
		tab, tab, tab, tab, tab, tab, tab, tab, tab);
	m_msgfmt.setTitle(buf);

	if(m_list!=NULL){
		while((m_ifstat = (scInterfaceStatus *)ll_element_at(m_list, at++))!=NULL){
			if(!instQ->isEmpty()){
				for(e=instQ->frontNode();e!=NULL;e=instQ->getNext(e)){
					char *instname = (char *)e->d;
					if(strcmp(instname, m_ifstat->ifinfo.ifname)==0){
						memset(buf, 0x00, sizeof(buf));
						sprintf(buf, "%s%c%lu%c%lu%c%lu%c%lu%c%lu%c%lu%c%lu%c%.02f%c%.02f\n",
							m_ifstat->ifinfo.ifname, tab,
							m_ifstat->inpkts, tab, m_ifstat->outpkts, tab,
							m_ifstat->inerrors, tab, m_ifstat->outerrors, tab,
							m_ifstat->collisions, tab, m_ifstat->inoctets , tab, m_ifstat->outoctets,
							tab, m_ifstat->inoctusage , tab, m_ifstat->outoctusage);
						m_msgfmt.addMessage(strdup(buf));
					}
				}
			}else{
				memset(buf, 0x00, sizeof(buf));
				sprintf(buf, "%s%c%lu%c%lu%c%lu%c%lu%c%lu%c%lu%c%lu%c%.02f%c%.02f\n",
					m_ifstat->ifinfo.ifname, tab,
					m_ifstat->inpkts, tab, m_ifstat->outpkts, tab,
					m_ifstat->inerrors, tab, m_ifstat->outerrors, tab,
					m_ifstat->collisions, tab, m_ifstat->inoctets , tab, m_ifstat->outoctets,
					tab, m_ifstat->inoctusage , tab, m_ifstat->outoctusage);
				m_msgfmt.addMessage(strdup(buf));
			}
		}
	}

	return;
}

void CIFPerfCollector::isOverThreshold(CItemCondition *cond)
{
	int at=0,i=0;
	char temp[32];
	bool b=false;

	if(cond->getElement() > 5) return;

	if(m_list!=NULL){
		while((m_ifstat = (scInterfaceStatus *)ll_element_at(m_list, at++))!=NULL){
			if(cond->getInstanceName() == "ALL" || cond->getInstanceName() == m_ifstat->ifinfo.ifname){
				/* check alarm */
				if(cond->getElement() == 1){ /* packet in */
					b = cond->isOverThreshold(m_ifstat->inpkts);
				}else if(cond->getElement() == 2) { /* packet out */
					b = cond->isOverThreshold(m_ifstat->outpkts);
				}else if(cond->getElement() == 3) { /* error in */
					b = cond->isOverThreshold(m_ifstat->inerrors);
				}else if(cond->getElement() == 4) { /* error out */
					b = cond->isOverThreshold(m_ifstat->outerrors);
				}else if(cond->getElement() == 5) { /* collision */
					b = cond->isOverThreshold(m_ifstat->collisions);
				}
				checkAlarm(cond, m_ifstat->ifinfo.ifname, b, m_ifstat);
			}
		}
	}

	return ;
}

void CIFPerfCollector::checkAlarm(CItemCondition *_cond, char *inst, bool ialarm, scInterfaceStatus *ifstat)
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
	sprintf(buf, "Instance%cPacketIn%cPacketOut%cPacketInError%cPacketOutError%cCollision%cOctIn%cOctOut%cOctInUsage(%)%cOctOutUsage(%)\n", 
		tab, tab, tab, tab, tab, tab, tab, tab, tab);
	msgfmt.setTitle(buf);

	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "%s%c%lu%c%lu%c%lu%c%lu%c%lu%c%lu%c%lu%c%.02f%c%.02f\n",
		ifstat->ifinfo.ifname, tab,
		ifstat->inpkts, tab, ifstat->outpkts, tab,
		ifstat->inerrors, tab, ifstat->outerrors, tab,
		ifstat->collisions, tab, ifstat->inoctets , tab, ifstat->outoctets,
		ifstat->inoctusage, tab, ifstat->outoctusage);
	msgfmt.addMessage(strdup(buf));

	msg = msgfmt.makeMessage();
	m_envvar->getEventQ()->enqueue(msg, NULL);		

	return;
}
