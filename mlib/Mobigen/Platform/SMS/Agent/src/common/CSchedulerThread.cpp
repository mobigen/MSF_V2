
#include "CMisc.h"
#include "CAgentEnvVar.h"
#include "CSchedulerThread.h"

using namespace OpenThreads;

void printLocalTime(time_t *t)
{
	struct tm *ltm = NULL;
	char buf[128];
	ltm = localtime(t);
	memset(buf, 0x00, sizeof(buf));
	strftime(buf, sizeof(buf)-1, "%Y-%m-%d %H:%M:%S", ltm);
	std::cout << "date : [" << buf << "]" << std::endl;
}

void CSchedulerThread::lock()
{
	pthread_mutex_lock(&m_lock);
}

void CSchedulerThread::unlock()
{
	pthread_mutex_unlock(&m_lock);
}
void CSchedulerThread::run()
{
	CAgentEnvVar *envvar = (CAgentEnvVar *)m_data;
	CAgentConfigVar *confvar = envvar->getAgentConfigVar();
	CQueue *policyQ = envvar->getPolicyQ();
	CQueue *itemlist = confvar->getItemQ();
	elem *e=NULL;
	CItem *item=NULL;
	unsigned long sec, usec, schd;
	time_t polltime;

	while(true) {
		lock();
		if(_quitflag == true) break;
		unlock();

		getTime(&sec, &usec);

		/* checking for schedule policy */
		for(e=itemlist->frontNode(); e!=NULL; e=itemlist->getNext(e)){
			item = (CItem *)e->d;
			polltime = item->getCollectTime();
			if(sec >= polltime && item->isCollect()==false && 
				item->isEnable() && item->isReportable() ){

				CPolicyItem *pollitem = new CPolicyItem();
				pollitem->setItem(item);
				pollitem->setPollType(TYPE_ACTIVE);
				pollitem->setPollTime(polltime);
				addInstanceToPollItem(pollitem, item);

				schd = item->getSchedule();
				polltime = (sec - (sec%schd)) + schd;
				item->setCollectTime(polltime);
				item->setIsCollect(true);
//std::cout << "ITEM : " << item->getCode() << std::endl;
				policyQ->enqueue(pollitem, NULL);
			}
		}

		/* checking for event schedule policy */
		for(e=itemlist->frontNode(); e!=NULL; e=itemlist->getNext(e)){
			item = (CItem *)e->d;
			polltime = item->getEventCollectTime();
			if(sec >= polltime && item->isCollect()==false && 
				item->isEnable() && item->isEnableEvent() ){

				CPolicyItem *pollitem = new CPolicyItem();
				pollitem->setItem(item);
				pollitem->setPollType(TYPE_EVENT);
				pollitem->setPollTime(polltime);
				addInstanceToPollItem(pollitem, item);

				schd = item->getEventSchedule();
				polltime = (sec - (sec%schd)) + schd;
				item->setEventCollectTime(polltime);
				item->setIsCollect(true);
//std::cout << "ITEM : " << item->getCode() << std::endl;
				policyQ->enqueue(pollitem, NULL);
			}
		}
		msleep(10);
	}

	Thread::Yield();
	notifyObserversFinished(getThreadId());

}

void CSchedulerThread::addInstanceToPollItem(CPolicyItem *pollitem, CItem *item)
{
	CQueue *instQ = item->getInstanceQ();
	CQueue *poll_instQ = pollitem->getInstQ();
	elem *e=NULL;
	CItemInstance *inst=NULL;

	for(e=instQ->frontNode(); e!=NULL; e=instQ->getNext(e))
	{
		inst = (CItemInstance *)e->d;
		poll_instQ->enqueue(strdup(inst->getValue().c_str()), NULL);
	}
}

void CSchedulerThread::quit() {
	lock();
	_quitflag = true;
	unlock();
}

void startSchedulerThread(void *data)
{

	CSchedulerThread *thread = new CSchedulerThread(data, 1);
	thread->start();

	return ;
}

