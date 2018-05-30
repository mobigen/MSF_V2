

#include "CHostConfCollector.h"


CHostConfCollector::CHostConfCollector()
{
	memset(m_ipaddr, 0x00, sizeof(m_ipaddr));
}

CHostConfCollector::~CHostConfCollector()
{
}

void CHostConfCollector::collect()
{
	char *msg=NULL;

	if(m_pollitem->getPollType() == TYPE_EVENT) {
		return;
	}

	m_coreview = m_envvar->getKernelCore()->getCoreView();
	if(	scCoreViewBasicInfo(m_coreview, &m_sysinfo)==SC_ERR ||
		gethostipaddr(m_ipaddr) == -1 ) 
	{
		m_envvar->getKernelCore()->returnCoreView(m_coreview);
		return;
	}
	m_hostid = gethostid();
	m_envvar->getKernelCore()->returnCoreView(m_coreview);

	makeMessage();
	msg = m_msgfmt.makeMessage();

	if(m_pollitem->getPollType() == TYPE_PASSIVE){
		m_envvar->getRespQ()->enqueue(msg, NULL);		
	}else{
		if(isShortPerf()==true){
			m_envvar->getShortPerfQ()->enqueue(msg, NULL);		
		}else{
			m_envvar->getLongPerfQ()->enqueue(msg, NULL);		
		}
	}
}

void CHostConfCollector::makeMessage()
{
	int i=0;
	char buf[1024], temp[32], tab=0x09;
	CQueue *instQ = m_pollitem->getInstQ();
	elem *e=NULL;

	m_msgfmt.setItem(m_pollitem->getItem());
	m_msgfmt.setPollTime(m_pollitem->getPollTime());
	m_msgfmt.setType(m_pollitem->getPollType());
	if(m_pollitem->getPollType()==TYPE_PASSIVE)
		m_msgfmt.setCommand((char *)m_pollitem->getCommand().c_str());

	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "HostName%cIPAddress%cOSType%cOSVersion%cModel%cHostID\n",
		tab, tab, tab, tab, tab);
	m_msgfmt.setTitle(buf);


	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "%s%c%s%c%s%c%s%c%s%c%x\n",
		m_sysinfo.hostname, tab, m_ipaddr, tab,
		m_sysinfo.osname, tab, m_sysinfo.release, tab,
		m_sysinfo.machine, tab, m_hostid);
	m_msgfmt.addMessage(strdup(buf));

	return;
}
