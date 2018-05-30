

#include "CIFConfCollector.h"


CIFConfCollector::CIFConfCollector()
{
	m_list = NULL;
}

CIFConfCollector::~CIFConfCollector()
{
	if(m_list!=NULL)
		scCoreViewRelease(&m_list);
}

void CIFConfCollector::collect()
{
	char *msg=NULL;

	if(m_pollitem->getPollType() == TYPE_EVENT) {
		return;
	}

	m_coreview = m_envvar->getKernelCore()->getCoreView();
	if(	(m_list = scCoreViewInterfaceStatus(m_coreview))==NULL ) {
		m_envvar->getKernelCore()->returnCoreView(m_coreview);
		return;
	}
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

void CIFConfCollector::makeMessage()
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
	//sprintf(buf, "Instance%cType%cSpeed(bps)%cMacAddress%cIPAddress\n", tab, tab, tab, tab);
	sprintf(buf, "Instance%cSpeed(bps)%cMacAddress%cIPAddress\n", tab, tab, tab, tab);
	m_msgfmt.setTitle(buf);

	if(m_list!=NULL){
		while((m_ifstat = (scInterfaceStatus *)ll_element_at(m_list, at++))!=NULL){
			if(!instQ->isEmpty()){
				for(e=instQ->frontNode();e!=NULL;e=instQ->getNext(e)){
					char *instname = (char *)e->d;
					if(strcmp(instname, m_ifstat->ifinfo.ifname)==0){
						memset(buf, 0x00, sizeof(buf));
						sprintf(buf, "%s%c%dMb%c%02x:%02x:%02x:%02x:%02x:%02x%c%s\n",
							m_ifstat->ifinfo.ifname, tab,
							m_ifstat->ifinfo.speed/1000000, tab,
							(m_ifstat->ifinfo.hwaddr[0] & 0377),
							(m_ifstat->ifinfo.hwaddr[1] & 0377),
							(m_ifstat->ifinfo.hwaddr[2] & 0377),
							(m_ifstat->ifinfo.hwaddr[3] & 0377),
							(m_ifstat->ifinfo.hwaddr[4] & 0377),
							(m_ifstat->ifinfo.hwaddr[5] & 0377), tab,
							inet_ntoa(m_ifstat->ifinfo.addr));
						m_msgfmt.addMessage(strdup(buf));
					}
				}
			}else{
				memset(buf, 0x00, sizeof(buf));
				sprintf(buf, "%s%c%dMb%c%02x:%02x:%02x:%02x:%02x:%02x%c%s\n",
					m_ifstat->ifinfo.ifname, tab,
					m_ifstat->ifinfo.speed/1000000, tab,
					(m_ifstat->ifinfo.hwaddr[0] & 0377),
					(m_ifstat->ifinfo.hwaddr[1] & 0377),
					(m_ifstat->ifinfo.hwaddr[2] & 0377),
					(m_ifstat->ifinfo.hwaddr[3] & 0377),
					(m_ifstat->ifinfo.hwaddr[4] & 0377),
					(m_ifstat->ifinfo.hwaddr[5] & 0377), tab,
					inet_ntoa(m_ifstat->ifinfo.addr));
				m_msgfmt.addMessage(strdup(buf));
			}
		}
	}

	return;
}
