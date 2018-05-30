
#include "CKernelCore.h"

CKernelCore::CKernelCore()
{
	m_coreview = scCoreViewCreate();
	pthread_mutex_init(&m_lock, NULL);
}


CKernelCore::~CKernelCore()
{
	scCoreViewDestroy(m_coreview);
	pthread_mutex_destroy(&m_lock);
}

void CKernelCore::lock()
{
	pthread_mutex_lock(&m_lock);
}

void CKernelCore::unlock()
{
	pthread_mutex_unlock(&m_lock);
}

scCoreView *CKernelCore::getCoreView()
{
	lock();
	return m_coreview;
}

void CKernelCore::returnCoreView(scCoreView *coreview)
{
	unlock();
}
