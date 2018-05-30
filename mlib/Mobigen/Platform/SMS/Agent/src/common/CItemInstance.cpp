
#include "CItemInstance.h"


CItemInstance::CItemInstance()
{
	m_name = "";
	m_dataQ = new CQueue();
}


CItemInstance::~CItemInstance()
{
	delete m_dataQ;
}


void deleteCItemInstance(void *d)
{
	CItemInstance *inst = (CItemInstance *)d;
	if(inst!=NULL) delete inst;
}


