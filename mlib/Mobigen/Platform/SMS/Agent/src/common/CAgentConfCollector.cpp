

#include "CAgentConfCollector.h"

using namespace std;

CAgentConfCollector::CAgentConfCollector()
{
}

CAgentConfCollector::~CAgentConfCollector()
{
}

void CAgentConfCollector::collect()
{
	char *msg=NULL;

	if(m_pollitem->getPollType() == TYPE_EVENT) {
		return;
	}

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


void CAgentConfCollector::makeMessage()
{
	char buf[1024], tab=0x09;
	CAgentConfigVar *confvar = m_envvar->getAgentConfigVar();

	m_msgfmt.setItem(m_pollitem->getItem());
	m_msgfmt.setPollTime(m_pollitem->getPollTime());
	m_msgfmt.setType(m_pollitem->getPollType());
	if(m_pollitem->getPollType()==TYPE_PASSIVE)
		m_msgfmt.setCommand((char *)m_pollitem->getCommand().c_str());

	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "DBTYPE%cDB_CONNECT_INFO%cEVENT_PORT%cSHORT_PORT%cLONG_PORT%cRESP_PORT%cCMD_PORT\n",
		tab, tab, tab, tab, tab, tab, tab);
	m_msgfmt.setTitle(buf);

	memset(buf, 0x00, sizeof(buf));
	if(confvar->getDBType()=="Oracle"){
		sprintf(buf, "%s%c%s/%s@%s%c%d%c%d%c%d%c%d%c%d\n",
			confvar->getDBType().c_str(), tab, confvar->getOraUID().c_str(),
			confvar->getOraPasswd().c_str(), confvar->getOraSID().c_str(), tab,
			confvar->getEventPort(), tab, confvar->getShortPerfPort(), tab,
			confvar->getLongPerfPort(), tab, confvar->getRespPort(), tab, confvar->getCmdPort());
	}else{
		sprintf(buf, "%s%c%s/%s@%s%c%d%c%d%c%d%c%d%c%d\n",
			"Unknown_DB", tab, confvar->getOraUID().c_str(),
			confvar->getOraPasswd().c_str(), confvar->getOraSID().c_str(), tab,
			confvar->getEventPort(), tab, confvar->getShortPerfPort(), tab,
			confvar->getLongPerfPort(), tab, confvar->getRespPort(), tab, confvar->getCmdPort());
	}
	m_msgfmt.addMessage(strdup(buf));
}

