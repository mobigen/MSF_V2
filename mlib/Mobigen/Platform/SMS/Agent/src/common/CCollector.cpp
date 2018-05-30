
#include "CCollector.h"


CCollector::CCollector()
{
	return;
}

bool CCollector::isShortPerf()
{
	if(m_pollitem->getItem()->getSchedule() >= 3600) return false;
	else return true;
}
