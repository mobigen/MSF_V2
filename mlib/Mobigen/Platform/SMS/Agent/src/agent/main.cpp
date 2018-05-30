
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include <time.h>
#include <signal.h>
#include <pthread.h>
#include <string>
#include <vector>
#include <deque>

#include "CAgentEnvVar.h"
#include "CSocketWorkerThread.h"
#include "CMisc.h"
#include "SCThread.h"
#include "CSchedulerThread.h"
#include "CKernelCore.h"
#include "CSyslogMonitorThread.h"


#include "StrUtil.h"
#include "PthTask.h"
#include "SecureProxy.h"

scCpuStatus g_ucpu, g_mcpu[SC_MAX_CPU_NUM];
int g_ncpu;
time_t g_cputime;

pthread_mutex_t g_session_lock;

void Usage(char **argv)
{
	printf("\nUsage :\n\t%s\n", argv[0]);
	exit(0);
}

void startProxyServer(int port)
{
    int s_port = port+6, t_port = port;
    string shared_key = "mobigen";
	string t_ip = "127.0.0.1";

    SecureProxyServer *s_proxy_server =
         new SecureProxyServer(s_port, t_ip, t_port, shared_key);
    s_proxy_server->set_auto_delete(true);
    s_proxy_server->start();
}

void initProcess()
{
	bool b=false;
	CAgentEnvVar env;
	CAgentConfigVar *cacv = env.getAgentConfigVar();
	CQueue *eventQ = env.getEventQ();
#if defined(ORACLE_ENABLE)
	CDBSession *dbsess = NULL;
#endif /* ORACLE_ENABLE */
	int i=0;

	signal(SIGCLD, SIG_IGN);
	signal(SIGCHLD, SIG_IGN);
	signal(SIGPIPE, SIG_IGN);

	cacv->loadXMLConfigVar();

	g_cputime = 0;
	memset(&g_ucpu, 0x00, sizeof(g_ucpu));
	memset(&g_mcpu, 0x00, sizeof(g_mcpu));

	/* 세션 상태 정보를 설정할 경우에 동기화로 사용될 키 */
	pthread_mutex_init(&g_session_lock, NULL);

#if defined(ORACLE_ENABLE)
	dbsess = new CDBSession;
	if(dbsess->connect(
		(char *)cacv->getOraUID().c_str(),
		(char *)cacv->getOraPasswd().c_str(),
		(char *)cacv->getOraSID().c_str()) < 0 )
	{
		fprintf(stderr, "connect to oracle [%s/%s/@%s] error!\n",
			cacv->getOraUID().c_str(), 
			cacv->getOraPasswd().c_str(), cacv->getOraSID().c_str());
	}else
		env.getDBPool()->putSession(dbsess);
#endif /* ORACLE_ENABLE */

	startSyslogThread((void *)&env, 1);
	sleep(1);
	startThreadWorker((void *)&env, 3);
	startSchedulerThread((void *)&env);

	startProxyServer(cacv->getEventPort());
	startSocketWorkerThread(&env, (void *)env.getEventQ(), env.getEventSession(), cacv->getEventPort(), SC_STREAM_TYPE_EVENT);

	startProxyServer(cacv->getShortPerfPort());
	startSocketWorkerThread(&env, (void *)env.getShortPerfQ(), env.getShortPerfSession(), cacv->getShortPerfPort(), SC_STREAM_TYPE_EVENT);

	startProxyServer(cacv->getLongPerfPort());
	startSocketWorkerThread(&env, (void *)env.getLongPerfQ(), env.getLongPerfSession(), cacv->getLongPerfPort(), SC_STREAM_TYPE_EVENT);

	startProxyServer(cacv->getRespPort());
	startSocketWorkerThread(&env, (void *)env.getRespQ(), env.getRespSession(), cacv->getRespPort(), SC_STREAM_TYPE_EVENT);

	startProxyServer(cacv->getCmdPort());
	startSocketWorkerThread(&env, (void *)&env, env.getCmdSession(), cacv->getCmdPort(), SC_STREAM_TYPE_COMMAND);

	startProxyServer(cacv->getSessionPort());
	startSocketWorkerThread(&env, (void *)&env, &b, cacv->getSessionPort(), SC_STREAM_TYPE_SESSION);

	while(1){
		msleep(5000);
	}
}

void initSignal()
{
	signal(SIGHUP, SIG_IGN);
	signal(SIGCHLD, SIG_IGN);
    signal(SIGPIPE, SIG_IGN);
}


int main(int argc, char **argv)
{

//	initDaemonProc();

	initSignal();
	initProcess();

	return 0;
}
