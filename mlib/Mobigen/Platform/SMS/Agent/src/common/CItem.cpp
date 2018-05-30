
#include "CItem.h"

CItem::CItem()
{
	m_code = "";
	m_name = "";
	m_schedule = 0;
	m_eventSchedule = 0;
	m_enable = "X";
	m_method = "XXX";

	m_collect = 0;
	m_eventCollect = 0;
	m_instQ = new CQueue();
	m_condQ = new CQueue();
	m_alarmInstanceQ = new CQueue();
	m_isCollect = false;
}

CItem::~CItem()
{
	delete m_instQ;
	delete m_condQ;
	delete m_alarmInstanceQ;
}


bool CItem::isEnable()
{
	if(m_enable == "O") return true;
	else return false;
}

bool CItem::isPassive()
{
	if((m_method.c_str())[0] == 'O') return true;
	else return false;
}

bool CItem::isReportable()
{
	if((m_method.c_str())[1] == 'O') return true;
	else return false;
}

bool CItem::isEnableEvent()
{
	if((m_method.c_str())[2] == 'O') return true;
	else return false;
}

void CItem::addInstance(CItemInstance *inst)
{
	m_instQ->enqueue(inst, deleteCItemInstance);
}

void CItem::addCondition(CItemCondition *cond)
{
	m_condQ->enqueue(cond, deleteCItemCondition);
}

void CItem::addAlarm(st_item_alarm *alarm)
{
	m_alarmInstanceQ->enqueue(alarm, NULL);
}

void CItem::delAlarm(st_item_alarm *alarm)
{
	st_item_alarm *_alarm=NULL;
	elem *e;

	for(e=m_alarmInstanceQ->frontNode();e!=NULL;e=m_alarmInstanceQ->getNext(e))
	{
		_alarm = (st_item_alarm *)e->d;
		if(strcmp(_alarm->instance, alarm->instance)==0 &&
			_alarm->condid == alarm->condid) {

			m_alarmInstanceQ->removeNode(e);
			return;
		}
	}
	return;
}

bool CItem::isAlarm(st_item_alarm *alarm)
{
	st_item_alarm *_alarm=NULL;
	elem *e;

	for(e=m_alarmInstanceQ->frontNode();e!=NULL;e=m_alarmInstanceQ->getNext(e))
	{
		_alarm = (st_item_alarm *)e->d;
		if(strcmp(_alarm->instance, alarm->instance)==0 &&
			_alarm->condid == alarm->condid) return true;
	}

	return false;
}

void deleteCItem(void *d)
{
	CItem *item = (CItem *)d;
	if(item != NULL) delete item;
}
