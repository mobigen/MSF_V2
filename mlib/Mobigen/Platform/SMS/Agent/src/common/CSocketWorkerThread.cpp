
#include <signal.h>
#include "CSocketWorkerThread.h"

unsigned char echo_off[3] = {TELNET_IAC, TELNET_WILL, TELNET_ECHO}; 
unsigned char echo_on[3]  = {TELNET_IAC, TELNET_WONT, TELNET_ECHO}; 

void CSocketWorkerThread::lock()
{
	pthread_mutex_lock(&m_lock);
}

void CSocketWorkerThread::unlock()
{
	pthread_mutex_unlock(&m_lock);
}

void CSocketWorkerThread::processEventMessage()
{
	CQueue *msgQ = (CQueue *)m_data;
	char *msg=NULL, onebit=0x00;
	int clisd = getClientSD(), nwrite, nread;
	char buf[1024];

	std::cout << "Client process accepted!!" << std::endl;

	while(true){

		msg = (char *)msgQ->dequeue();
		if(msg!=NULL){
//			if((nwrite = ::write(clisd, msg, strlen(msg)))==-1){
			if((nwrite = ::send(clisd, msg, strlen(msg), 0))==-1){
				fprintf(stderr, "[%s,%d] socket send error[%s]\n", __FUNCTION__, __LINE__, strerror(errno));
				std::cout << "msg push : [" << msg << "]" << std::endl;
				msgQ->push(msg, NULL);
				close_cli();
				return;
			}

//			std::cout << "send msg : [" << msg << "][" << nwrite << "]" << std::endl;

			if(msg!=NULL) { free(msg); msg = (char *)NULL; }
			continue;
		}

		memset(buf, 0x00, sizeof(buf));
		if((nread = readn(clisd, buf, sizeof(buf)-1, 1))>0){
			if(strncmp(buf, "exit", 4)==0){
				close_cli();
				return;
			}
		}

		if(::write(clisd, &onebit, 1) == -1){
			fprintf(stderr, "socket error[%s]\n", strerror(errno));
			close_cli();
			return;
		}

	}
}

void CSocketWorkerThread::processCommandMessage()
{
	CAgentEnvVar *envvar = (CAgentEnvVar *)m_data;
	char buffer[4096], tmp_buffer[4096], block[4096], msg[1024], onebit=0x00;
	char *p=NULL, *q=NULL;
	int clisd = getClientSD(), nread, len;
	CProtocolProcessor cp;
	cp.setEnvVar(envvar);

	std::cout << "Client process accepted!!" << std::endl;
	std::cout << "Command mode thread!!" << std::endl;
	memset(buffer, 0x00, sizeof(buffer));

	while(true){

		memset(msg, 0x00, sizeof(msg));
		if((nread = readn(clisd, msg, sizeof(msg)-1, 1))>0){
			if(strncmp(msg, "exit", 4)==0){
				close_cli();
				return;
			}
			strcat(buffer, msg);
			if((p = (char *)strchr(buffer, ';'))!=NULL){
				memset(block, 0x00, sizeof(block));
				len = strlen(buffer)-strlen(p);
				strncpy(block, buffer, len);
				p++;
				memset(tmp_buffer, 0x00, sizeof(tmp_buffer));
				strcpy(tmp_buffer, p);
				memset(buffer, 0x00, sizeof(buffer));
				strcpy(buffer, tmp_buffer);
				cp.process(block);
			}
		}

		if(::write(clisd, &onebit, 1) == -1){
			fprintf(stderr, "socket error[%s]\n", strerror(errno));
			close_cli();
			return;
		}

		msleep(10);
	}
}

void CSocketWorkerThread::processSessionStatus()
{
	CAgentEnvVar *envvar = (CAgentEnvVar *)m_data;
	char buffer[4096], sztime[32], hname[128], tab=0x09;
	int clisd = getClientSD(), nread, len;
	time_t curtime;
	struct tm *ptm=NULL;

	memset(buffer, 0x00, sizeof(buffer));
	memset(sztime, 0x00, sizeof(sztime));
	memset(hname, 0x00, sizeof(hname));

	gethostname(hname, sizeof(hname)-1);
	time(&curtime);
	ptm = localtime(&curtime);
	strftime(sztime, sizeof(sztime)-1, "%Y-%m-%d %H:%M:%S", ptm);

	pthread_mutex_lock(&g_session_lock);

	sprintf(buffer, "%s%c%s\n"
					"AgentSessionStatus%cMonitor Agent Session Status\n"
					"Name%cStatus%cMessages\n"
					"Event%c%s%c%d\n"
					"ShortPerf%c%s%c%d\n"
					"LongPerf%c%s%c%d\n"
					"Response%c%s%c%d\n"
					"Command%c%s%c%d\n"
					"COMPLETED\n",
					hname, tab, sztime,
					tab, 
					tab, tab,
					tab, *(envvar->getEventSession())==true? "CONNECTED":"NOT CONNECTED", tab, envvar->getEventQ()->size(),
					tab, *(envvar->getShortPerfSession())==true? "CONNECTED":"NOT CONNECTED", tab, envvar->getShortPerfQ()->size(),
					tab, *(envvar->getLongPerfSession())==true? "CONNECTED":"NOT CONNECTED", tab, envvar->getLongPerfQ()->size(),
					tab, *(envvar->getRespSession())==true? "CONNECTED":"NOT CONNECTED", tab, envvar->getRespQ()->size(),
					tab, *(envvar->getCmdSession())==true? "CONNECTED":"NOT CONNECTED", tab, envvar->getCmdQ()->size());

	pthread_mutex_unlock(&g_session_lock);

	::write(clisd, buffer, strlen(buffer));
	close_cli();
	return;
}

void CSocketWorkerThread::run()
{

    signal(SIGCLD, SIG_IGN);
    signal(SIGCHLD, SIG_IGN);
    signal(SIGPIPE, SIG_IGN);

	if(create()==false){
		fprintf(stderr, "create socket error[%s]\n", strerror(errno));
		exit(1);
	}

	if(bind(m_port)==false){
		fprintf(stderr, "socket bind error[%s]\n", strerror(errno));
		exit(1);
	}

	if(listen()==false){
		fprintf(stderr, "socket listen error[%s]\n", strerror(errno));
		exit(1);
	}

	while(true) {
		if(accept()==false) continue;

        signal(SIGCLD, SIG_IGN);
        signal(SIGCHLD, SIG_IGN);
        signal(SIGPIPE, SIG_IGN);

		if(login()==false){
			close_cli();
			continue;
		}
		pthread_mutex_lock(&g_session_lock);
		*m_session_status = true;
		pthread_mutex_unlock(&g_session_lock);
		if(m_type == SC_STREAM_TYPE_EVENT)
			processEventMessage();
		else if(m_type == SC_STREAM_TYPE_COMMAND)
			processCommandMessage();
		else if(m_type == SC_STREAM_TYPE_SESSION)
			processSessionStatus();
		pthread_mutex_lock(&g_session_lock);
		*m_session_status = false;
		pthread_mutex_unlock(&g_session_lock);
	}
}

bool CSocketWorkerThread::login() {

	int clisd = getClientSD(), nread, len, maxlogin=3, i=0;
	std::string uid = m_envvar->getAgentConfigVar()->getUserid();
	std::string passwd = m_envvar->getAgentConfigVar()->getPasswd();
	std::string accessip = m_envvar->getAgentConfigVar()->getAccessIP();
	char remoteip[128], _remoteip[128], temp[128], buffer[1024];
	char *p=NULL, *q=NULL;
	char _uid[128], _passwd[128], en_passwd[128];
	struct termio tdes;

	memset(remoteip, 0x00, sizeof(remoteip));
	memset(_remoteip, 0x00, sizeof(_remoteip));
	p = (char *)strchr(accessip.c_str(), '*');
	if(p!=NULL){
		strncpy(_remoteip, accessip.c_str(),
			strlen(accessip.c_str())-strlen(p));
	}else
		strcpy(_remoteip, accessip.c_str());

	strcpy(remoteip, inet_ntoa(m_addr.sin_addr));

	if(strncmp(_remoteip, remoteip, strlen(_remoteip))!=0){
		memset(buffer, 0x00, sizeof(buffer));
		strcpy(buffer, "-ERR Invalid IP Address!\r\n");
		if(::send(clisd, buffer, strlen(buffer), 0)<0) return false;
		return false;
	}else{
		memset(buffer, 0x00, sizeof(buffer));
		strcpy(buffer, "+OK Welcome!\r\n");
		if(::send(clisd, buffer, strlen(buffer), 0)<0) return false;
	}

	memset(buffer, 0x00, sizeof(buffer));
	memset(_uid, 0x00, sizeof(_uid));
	memset(_passwd, 0x00, sizeof(_passwd));

	if((nread = recv(clisd, buffer, sizeof(buffer)-1, MSG_PEEK))<0) return false;
	if((nread = readn(clisd, buffer, nread, 1))<0) return false;

	p = buffer; p+=(strlen(buffer)-1);
	if(*p=='\n') *p='\0';
	if(*(p-1) == '\r') *(p-1)='\0';

	if((q=(char *)strstr(buffer, "USER"))!=NULL){
		q+=4;
		while(isspace(*q)) q++;
		strcpy(_uid, q);
	}

	if(q==NULL || uid != _uid)
	{
		memset(buffer, 0x00, sizeof(buffer));
		sprintf(buffer, "-ERR Invalid USER ID\r\n");
		if(::send(clisd, buffer, strlen(buffer), 0)<0) return false;
		return false;
	}else{
		memset(buffer, 0x00, sizeof(buffer));
		strcpy(buffer, "+OK USER success!\r\n");
		if(::send(clisd, buffer, strlen(buffer), 0)<0) return false;
	}

	memset(buffer, 0x00, sizeof(buffer));

	if((nread = recv(clisd, buffer, sizeof(buffer)-1, MSG_PEEK))<0){
		return false;
	}
	if((nread = readn(clisd, buffer, nread, 1))<0) return false;

	p = buffer; p+=(strlen(buffer)-1);
	if(*p=='\n') *p='\0';
	if(*(p-1) == '\r') *(p-1)='\0';

	if((q=(char *)strstr(buffer, "PASS"))!=NULL){
		q+=4;
		while(isspace(*q)) q++;
		strcpy(_passwd, q);
	}

	memset(en_passwd, 0x00, sizeof(en_passwd));
	MD5::encode(_passwd, en_passwd);

	if(q==NULL || passwd != en_passwd)
	{
		memset(buffer, 0x00, sizeof(buffer));
		sprintf(buffer, "-ERR Invalid password\r\n");
		if(::send(clisd, buffer, strlen(buffer), 0)<0) return false;
		return false;
	}else{
		memset(buffer, 0x00, sizeof(buffer));
		strcpy(buffer, "+OK Login success!\r\n");
		if(::send(clisd, buffer, strlen(buffer), 0)<0) return false;
		return true;
	}
}

void CSocketWorkerThread::quit() {
	lock();
	_quitflag = true;
	unlock();
}

void startSocketWorkerThread(CAgentEnvVar *envvar, void *data, bool *b, int port, int type)
{
	CSocketWorkerThread *thread = new CSocketWorkerThread(envvar, data, b, port, 1, type);
	thread->start();

	return ;
}

