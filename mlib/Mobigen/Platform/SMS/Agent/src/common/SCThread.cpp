
#include "CMisc.h"
#include "CAgentEnvVar.h"
#include "SCThread.h"

void SCThread::lock()
{
	pthread_mutex_lock(&m_lock);
}

void SCThread::unlock()
{
	pthread_mutex_unlock(&m_lock);
}

void SCThread::run()
{
	CAgentEnvVar *envvar = (CAgentEnvVar *)m_data;
	CQueue *policyQ = envvar->getPolicyQ();
	elem *e=NULL;
	CPolicyItem *pollitem=NULL;

	while(true) {
		lock();
		if(_quitflag == true) break;
		unlock();

		pollitem = (CPolicyItem *)policyQ->dequeue();
		if(pollitem!=NULL){
			invokeCollector(pollitem);
			pollitem->getItem()->setIsCollect(false);
			delete pollitem;
		}

		msleep(10);
	}

	Thread::Yield();
	notifyObserversFinished(getThreadId());

}

void SCThread::invokeCollector(CPolicyItem *pollitem)
{
	CCollector *collector=NULL;
	std::string itemcode = pollitem->getItem()->getCode();

//std::cout << "invoke : " << itemcode << std::endl;
	if(itemcode == "CPUPerf")
		collector = new CCPUPerfCollector();
	else if(itemcode == "PatchConf")
		collector = new CPatchConfCollector();
	else if(itemcode == "SWConf")
		collector = new CSWConfCollector();
	else if(itemcode == "CPUConf")
		collector = new CCPUConfCollector();
	else if(itemcode == "MemoryConf")
		collector = new CMemoryConfCollector();
	else if(itemcode == "DiskConf")
		collector = new CDiskConfCollector();
	else if(itemcode == "HostConf")
		collector = new CHostConfCollector();
	else if(itemcode == "InterfaceConf")
		collector = new CIFConfCollector();
	else if(itemcode == "CPULoad")
		collector = new CCPULoadPerfCollector();
	else if(itemcode == "MemoryPerf")
		collector = new CMemoryPerfCollector();
	else if(itemcode == "DiskPerf")
		collector = new CDiskPerfCollector();
	else if(itemcode == "DiskIOPerf")
		collector = new CDiskIOPerfCollector();
	else if(itemcode == "NetworkPerf")
		collector = new CIFPerfCollector();
	else if(itemcode == "ProcessPerf")
		collector = new CProcessPerfCollector();
	else if(itemcode == "TopMemProcess")
		collector = new CTopMemoryProcessPerfCollector();
	else if(itemcode == "TopCPUProcess")
		collector = new CTopCPUProcessPerfCollector();
	else if(itemcode == "LogCheck")
		collector = new CLogCheckCollector();
	else if(itemcode == "ShellCommand")
		collector = new CShellCommandCollector();
	else if(itemcode == "SessionPerf")
		collector = new CNetworkSessionCollector();
	else if(itemcode == "AgentConf")
		collector = new CAgentConfCollector();
	else if(itemcode == "ProcessHealth")
		collector = new CProcessHealthCollector();
#if defined(ORACLE_ENABLE)
	else if(itemcode == "OracleConf")
		collector = new COraConfCollector();
	else if(itemcode == "OraHitRatio")
		collector = new COraHitRatioCollector();
	else if(itemcode == "OraTopSql")
		collector = new COraTopSqlCollector();
	else if(itemcode == "OraSessionCount")
		collector = new COraSessionCountCollector();
	else if(itemcode == "OraDBLink")
		collector = new COraDBLinkCollector();
	else if(itemcode == "OraTableSpace")
		collector = new COraTableSpaceCollector();
	else if(itemcode == "OraRollback")
		collector = new COraRollbackCollector();
#endif /* ORACLE_ENABLE */
	else
		return;

	collector->setEnvVar((CAgentEnvVar *)m_data);
	collector->setPolicyItem(pollitem);
	collector->collect();
	
	delete collector;
	return;
}

void SCThread::quit() {
	lock();
	//_quitmutex.lock();
	_quitflag = true;
	//_quitmutex.unlock();
	unlock();
}

void startThreadWorker(void *data, int thread_num)
{

    int NUM_THREADS = thread_num;
    
	//std::cout << "Root Thread ID: " << getpid() << std::endl;
    
    //GLOBAL_NUM_THREADS = NUM_THREADS + 1;
    
    SCThreadObserver observer;
    register int i;

    std::vector<SCThread *> threads;

    OpenThreads::Thread::SetConcurrency(NUM_THREADS);

    OpenThreads::Thread::Init();
    for(i=0; i<NUM_THREADS; ++i) {
        int status;
        SCThread *thread = new SCThread(data, NUM_THREADS);
        threads.push_back(thread);
        thread->addObserver(&observer);
		thread->setStackSize(1024*256);
        status = thread->start();
        assert(status == 0);
    }

#if 0 /* to end thread worker */
	std::cout << "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz" << std::endl;
    bar.block(GLOBAL_NUM_THREADS);  // Block 'till ready
    bar.block(GLOBAL_NUM_THREADS);  // Block 'till finished

    char val;
    std::cout << "Press any key + return to quit." << std::endl;
    std::cin >> val;

    // Notify the threads to quit, wait for this to happen.
    for(i=0;i<threads.size();++i) {
        SCThread *thread = threads[i];
        thread->quit();
    }

    while(observer.getFinishedCount() != NUM_THREADS) {
        // Spin our wheels.
    }

    std::cout << std::endl;

    // Delete all the threads.
    for(i=0;i<threads.size();++i) {
        SCThread *thread = threads[i];
        delete thread;
    }

    threads.clear();
#endif

	return ;
}

#if 0
int main(int argc, char **argv) {

    if(argc != 2) {
        std::cout << "Usage: simpleThreader [NUM_THREADS] " 
		  << std::endl;
        return 0;
    };

	startThreadWorker((void *)"hello, world\n", atoi(argv[1]));

	std::cout << "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz" << std::endl;

	while(true){
		;;
	}
	return 0;
}

#endif
