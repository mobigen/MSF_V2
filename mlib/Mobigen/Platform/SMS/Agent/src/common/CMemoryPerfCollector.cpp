

#include "CMemoryPerfCollector.h"
#include "CAlarmProcessor.h"


CMemoryPerfCollector::CMemoryPerfCollector()
{
}

CMemoryPerfCollector::~CMemoryPerfCollector()
{
}

void CMemoryPerfCollector::collect()
{
	char *msg=NULL;

	m_coreview = m_envvar->getKernelCore()->getCoreView();
	if(	scCoreViewMemStatus(m_coreview, &m_memstat)==SC_ERR ||
		scCoreViewVMStatus(m_coreview, &m_vmstat)==SC_ERR )
	{
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

void CMemoryPerfCollector::makeMessage()
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
	sprintf(buf, 	"TotalPhysicalMemory(KB)%cFreePhysicalMemory(KB)%c"
					"PhysicalMemoryUsage(%%)%cTotalSwapMemory(KB)%c"
					"FreeSwapMemory(KB)%cSwapMemoryUsage(%%)%c"
					"PageScan(Count)%cPageOut(Count)%cSwapOut(Count)\n",
					tab, tab, tab, tab, tab, tab, tab, tab);
	m_msgfmt.setTitle(buf);

	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "%d%c%d%c%.02f%c%d%c%d%c%.02f%c%d%c%d%c%d\n",
			m_memstat.m_total, tab, m_memstat.m_total-m_memstat.m_used, tab,
			m_memstat.m_usage, tab, m_memstat.s_total, tab,
			m_memstat.s_total - m_memstat.s_used, tab,
			m_memstat.s_usage, tab, m_vmstat.scanrate, tab,
			m_vmstat.pageout, tab, m_vmstat.swapout);
	m_msgfmt.addMessage(strdup(buf));

	return;
}


void CMemoryPerfCollector::isOverThreshold(CItemCondition *cond)
{
	int at=0,i=0;
	char temp[32];
	bool b=false;

	if(cond->getElement() > 8) return;

	memset(temp, 0x00, sizeof(temp));

	/* check alarm */
	if(cond->getElement() == 0) { /* TotalPhysicalMemory */
		b = cond->isOverThreshold(m_memstat.m_total);
		strcpy(temp, "TotalPhysicalMemory");
	} else if(cond->getElement() == 1) { /* FreePhysicalMemory */
		b = cond->isOverThreshold(m_memstat.m_total-m_memstat.m_used);
		strcpy(temp, "FreePhysicalMemory");
	} else if(cond->getElement() == 2) { /* PhysicalMemoryUsage */
		b = cond->isOverThreshold(m_memstat.m_usage);
		strcpy(temp, "PhysicalMemoryUsage");
	} else if(cond->getElement() == 3) { /* TotalSwapMemory */
		b = cond->isOverThreshold(m_memstat.s_total);
		strcpy(temp, "TotalSwapMemory");
	} else if(cond->getElement() == 4) { /* FreeSwapMemory */
		b = cond->isOverThreshold(m_memstat.s_total - m_memstat.s_used);
		strcpy(temp, "FreeSwapMemory");
	} else if(cond->getElement() == 5) { /* SwapMemoryUsage */
		b = cond->isOverThreshold(m_memstat.s_usage);
		strcpy(temp, "SwapMemoryUsage");
	} else if(cond->getElement() == 6) { /* PageScan */
		b = cond->isOverThreshold(m_vmstat.scanrate);
		strcpy(temp, "PageScan");
	} else if(cond->getElement() == 7) { /* PageOut */
		b = cond->isOverThreshold(m_vmstat.pageout);
		strcpy(temp, "PageOut");
	} else if(cond->getElement() == 8) { /* SwapOut */
		b = cond->isOverThreshold(m_vmstat.swapout);
		strcpy(temp, "SwapOut");
	}
	checkAlarm(cond, temp, b);

	return ;
}

void CMemoryPerfCollector::checkAlarm(CItemCondition *_cond, char *inst, bool ialarm)
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
	sprintf(buf, 	"INSTANCE%cTotalPhysicalMemory(KB)%cFreePhysicalMemory(KB)%c"
					"PhysicalMemoryUsage(%%)%cTotalSwapMemory(KB)%c"
					"FreeSwapMemory(KB)%cSwapMemoryUsage(%%)%c"
					"PageScan(Count)%cPageOut(Count)%cSwapOut(Count)\n",
					tab, tab, tab, tab, tab, tab, tab, tab, tab);
	msgfmt.setTitle(buf);




	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "%s%c%d%c%d%c%.02f%c%d%c%d%c%.02f%c%d%c%d%c%d\n",
			inst, tab,
			m_memstat.m_total, tab, m_memstat.m_total-m_memstat.m_used, tab,
			m_memstat.m_usage, tab, m_memstat.s_total, tab,
			m_memstat.s_total - m_memstat.s_used, tab,
			m_memstat.s_usage, tab, m_vmstat.scanrate, tab,
			m_vmstat.pageout, tab, m_vmstat.swapout);
	msgfmt.addMessage(strdup(buf));

	msg = msgfmt.makeMessage();
	m_envvar->getEventQ()->enqueue(msg, NULL);		

	return;
}