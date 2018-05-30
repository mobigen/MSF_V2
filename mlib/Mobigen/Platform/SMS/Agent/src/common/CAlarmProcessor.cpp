
#include "CAlarmProcessor.h"



void CAlarmProcessor::check()
{
	CQueue *condQ = m_collector->getPolicyItem()->getItem()->getConditionQ();
	CItemCondition *cond=NULL;
	elem *e=NULL;

	for(e=condQ->frontNode();e!=NULL;e=condQ->getNext(e))
	{
		cond = (CItemCondition *)e->d;
		checkAlarm(cond);
	}
	return;
}

void CAlarmProcessor::checkAlarm(CItemCondition *cond)
{
	m_collector->isOverThreshold(cond);
	return;
}
