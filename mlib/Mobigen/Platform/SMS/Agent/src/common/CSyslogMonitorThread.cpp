
#include "CMisc.h"
#include "CAgentEnvVar.h"
#include "CSyslogMonitorThread.h"

void CSyslogMonitorThread::lock()
{
	pthread_mutex_lock(&m_lock);
}

void CSyslogMonitorThread::unlock()
{
	if(m_fd!=NULL) fclose(m_fd);
	pthread_mutex_unlock(&m_lock);
}

void CSyslogMonitorThread::run()
{
	char buf[1024];
	m_fd = NULL;
	m_offset=0;

	m_envvar = (CAgentEnvVar *)m_data;
	m_item = m_envvar->getAgentConfigVar()->getItem("Syslog");
	if(	m_item == NULL || m_item->isEnable()==false ||
		m_item->isEnableEvent()==false || m_item->getInstanceQ()->isEmpty()==true) return;
	m_filename = ((CItemInstance *)m_item->getInstanceQ()->frontNode()->d)->getValue();
	if((m_fd = fopen(m_filename.c_str(), "r"))==NULL){
		fprintf(stderr, "[%s,%d] file[%s] open error[%s]\n",__FUNCTION__, __LINE__, m_filename.c_str(), strerror(errno));
	}
	if(m_fd!=NULL){
		struct stat sbuf;
		stat(m_filename.c_str(), &sbuf);
		m_offset = sbuf.st_size;
		fseek(m_fd, 0, SEEK_END);
	}

	while(true) {

		checkFD();

		if(m_fd!=NULL){
			memset(buf, 0x00, sizeof(buf));
			while(fgets(buf, sizeof(buf)-1, m_fd)){
				m_offset += strlen(buf);
				buf[strlen(buf)-1] = 0x00;
				checkCondition(buf);
				memset(buf, 0x00, sizeof(buf));
			}
		}

		checkFD();

		msleep(10);
	}

	Thread::Yield();
	notifyObserversFinished(getThreadId());
}

void CSyslogMonitorThread::checkCondition(char *log)
{
	CQueue *condq = m_item->getConditionQ();
	elem *e=NULL;

	for(e=condq->frontNode();e!=NULL;e=condq->getNext(e)){
		CItemCondition *cond = (CItemCondition *)e->d;
		if(	cond->getInstanceName()=="ALL" || 
			cond->getInstanceName()==m_filename ){

			if(cond->isOverThreshold(log)==true){
				sendEvent(cond, log);
			}
		}
	}
}

void CSyslogMonitorThread::sendEvent(CItemCondition *cond, char *log)
{
	char tab=0x09;
	CMessageFormatter msgfmt;
	char msg[1024];
	time_t curtime; time(&curtime);

	msgfmt.setItem(m_item);
	msgfmt.setPollTime(curtime);
	msgfmt.setType(TYPE_EVENT);
	msgfmt.setItemCondition(cond);
	msgfmt.setEventStatus(true);

	memset(msg, 0x00, sizeof(msg));
	sprintf(msg, "Instance%cMessages\n", tab);
	msgfmt.setTitle(msg);

	memset(msg, 0x00, sizeof(msg));
	sprintf(msg, "%s%c%s\n", m_filename.c_str(), tab, log);
	msgfmt.addMessage(strdup(msg));

	m_envvar->getEventQ()->enqueue(msgfmt.makeMessage(), NULL);

	return;
}

void CSyslogMonitorThread::checkFD() {

	struct stat sbuf;	

	memset(&sbuf, 0x00, sizeof(struct stat));
	if(stat(m_filename.c_str(), &sbuf)<0){
		if(m_fd!=NULL) { fclose(m_fd); m_fd = NULL; }
		return ;
	}

	if(m_fd==NULL || m_offset > sbuf.st_size){
		if(m_fd!=NULL) fclose(m_fd);
		m_fd = fopen(m_filename.c_str(), "r");
		m_offset = 0;
	}

	return;
}

void CSyslogMonitorThread::quit() {
	lock();
	//_quitmutex.lock();
	_quitflag = true;
	//_quitmutex.unlock();
	unlock();
}

void startSyslogThread(void *data, int thread_num)
{

    int NUM_THREADS = thread_num;
    
    SCThreadObserver observer;
    register int i;

    std::vector<CSyslogMonitorThread *> threads;

    OpenThreads::Thread::SetConcurrency(NUM_THREADS);

    OpenThreads::Thread::Init();
    for(i=0; i<1; ++i) {
        int status;
        CSyslogMonitorThread *thread = new CSyslogMonitorThread(data, NUM_THREADS);
        threads.push_back(thread);
        thread->addObserver(&observer);
		thread->setStackSize(1024*256);
        status = thread->start();
        assert(status == 0);
    }

	return ;
}

