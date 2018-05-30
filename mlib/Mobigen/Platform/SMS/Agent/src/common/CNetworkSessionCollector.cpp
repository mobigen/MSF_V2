

#include "CNetworkSessionCollector.h"


CNetworkSessionCollector::CNetworkSessionCollector()
{
	m_list = NULL;
}

CNetworkSessionCollector::~CNetworkSessionCollector()
{
	if(m_list!=NULL)
		scCoreViewRelease(&m_list);
}

void CNetworkSessionCollector::collect()
{
	char *msg=NULL;

	if(m_pollitem->getPollType() == TYPE_EVENT) {
		return;
	}

	m_coreview = m_envvar->getKernelCore()->getCoreView();
	m_list = scCoreViewTCPInfo(m_coreview,0);
	m_envvar->getKernelCore()->returnCoreView(m_coreview);

	if (m_list == NULL) {
		return;
	}

	makeMessage();
	msg = m_msgfmt.makeMessage();

	if(m_pollitem->getPollType() == TYPE_PASSIVE){
		m_envvar->getRespQ()->enqueue(msg, NULL);		
	} else {
		if(isShortPerf()==true){
			m_envvar->getShortPerfQ()->enqueue(msg, NULL);		
		}else{
			m_envvar->getLongPerfQ()->enqueue(msg, NULL);		
		}
	}
}

void CNetworkSessionCollector::makeMessage()
{
	int i=0, at=0;
	char buf[1024], temp[32], tab=0x09;
	CQueue *instQ = m_pollitem->getInstQ();
	elem *e=NULL;

	m_msgfmt.setItem(m_pollitem->getItem());
	m_msgfmt.setPollTime(m_pollitem->getPollTime());
	m_msgfmt.setType(m_pollitem->getPollType());
	if(m_pollitem->getPollType()==TYPE_PASSIVE)
		m_msgfmt.setCommand((char *)m_pollitem->getCommand().c_str());

	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "LocalIP%cLocalPort%cRemoteIP%cRemotePort%cStatus\n", tab, tab, tab, tab);
	m_msgfmt.setTitle(buf);

	if(m_list!=NULL){
		while((m_tcpinfo = (scTCPInfo *)ll_element_at(m_list, at++))!=NULL){
			memset(buf, 0x00, sizeof(buf));

			char localIp[BUFSIZ], remoteIp[BUFSIZ];
			strcpy(localIp, inet_ntoa(m_tcpinfo->localaddr));
			strcpy(remoteIp,inet_ntoa(m_tcpinfo->remoteaddr));
			
			sprintf(buf, "%s%c%d%c%s%c%d%c%s\n",
				localIp, tab,
				ntohs(m_tcpinfo->localport), tab,
				remoteIp, tab,
				ntohs(m_tcpinfo->remoteport), tab,
				scCoreViewTCPStatus2redable(m_tcpinfo->state));
			m_msgfmt.addMessage(strdup(buf));
		}
	}

	return;
}

