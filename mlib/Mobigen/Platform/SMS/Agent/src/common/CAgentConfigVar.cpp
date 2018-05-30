
#include "CAgentConfigVar.h"

CAgentConfigVar::CAgentConfigVar()
{
	pthread_mutex_init(&m_lock, NULL);
	m_itemQ = new CQueue();
}

CAgentConfigVar::~CAgentConfigVar()
{
	pthread_mutex_destroy(&m_lock);
	delete m_itemQ;
}

void CAgentConfigVar::loadXMLConfigVar()
{
	char config_path[256];
	TiXmlNode *node=NULL, *nodeItem=NULL, *nodeContent=NULL, *nodeParam=NULL;
	TiXmlElement *elementParam=NULL;
	std::string paramName;
	time_t curtime, schd;

	memset(config_path, 0x00, sizeof(config_path));

#ifdef CYGWIN
	sprintf(config_path, "c:/scagent/conf/scagent.xml");
#else
	sprintf(config_path, "%s/conf/scagent.xml", getenv("AGENT_HOME"));
#endif
	m_doc = new TiXmlDocument(config_path);

	if(m_doc->LoadFile()==false){
		fprintf(stderr, "load xml configuration file  error![%s]\n", strerror(errno));
		exit(1);
	}

    // debug
    //m_doc->Print();

        
	//elementParam = m_doc->FirstChild("envvar")->ToElement();	
	elementParam = m_doc->FirstChildElement("envvar");


	m_eventport = atoi(elementParam->Attribute("eventport"));
	m_shortperfport = atoi(elementParam->Attribute("shortperfport"));
	m_longperfport = atoi(elementParam->Attribute("longperfport"));
	m_respport = atoi(elementParam->Attribute("respport"));
	m_cmdport = atoi(elementParam->Attribute("cmdport"));
	m_sessionport = atoi(elementParam->Attribute("sessionport"));

	elementParam = m_doc->FirstChild("config")->ToElement();

	if (elementParam->Attribute("DBTYPE") != NULL) {
		setDBType((char *)elementParam->Attribute("DBTYPE"));
	} else {
		setDBType("None");
	}

	setOraUID((char *)elementParam->Attribute("ORADBA"));
	setOraSID((char *)elementParam->Attribute("ORASID"));
	setOraPasswd((char *)elementParam->Attribute("ORAPW"));

	elementParam = m_doc->FirstChild("userinfo")->ToElement();
	setUserid((char *)elementParam->Attribute("userid"));
	setPasswd((char *)elementParam->Attribute("password"));
	setAccessIP((char *)elementParam->Attribute("accessip"));

	node = (m_doc->FirstChild( "config" ))->FirstChild(); // find first Item
	while(!(node->NoChildren())){
		// create new item.
		CItem *item = new CItem();
		nodeItem = node; // keep current pointer to find next item.

		node = node->FirstChild();
		while(!(node->NoChildren())){
			std::string content = node->Value();
			nodeContent = node; // kill current pointer to find next instances or conditions node.

			while(!(node->NoChildren())){
				paramName = node->Value();
				node = node->FirstChild();
				std::string value = node->Value();
				
				// set item value
				if(content == "code") item->setCode(value);
				else if(content == "name") item->setName(value);
				else if(content == "schedule") item->setSchedule((unsigned long)atoi(value.c_str()));
				else if(content == "eschedule") item->setEventSchedule((unsigned long)atoi(value.c_str()));
				else if(content == "enable") item->setEnable(value);
				else if(content == "method") item->setMethod(value);

				// set instance or condition value.
				while(paramName == "conditions" || paramName == "instances"){
					nodeParam = node;
					node = node->FirstChild();
					std::string paramval = node->Value();

					node = nodeParam;
					elementParam = node->ToElement();

					if(paramName == "conditions"){
						CItemCondition *cond = new CItemCondition();
						cond->setIndex((unsigned int)atoi(elementParam->Attribute("id")));
						cond->setInstanceName(elementParam->Attribute("instance"));
						cond->setElement((unsigned int)atoi(elementParam->Attribute("element")));
						cond->setSeverity(elementParam->Attribute("level"));
						cond->setCondition(paramval);

						item->addCondition(cond);
					}else if(paramName == "instances"){
						CItemInstance *inst = new CItemInstance;

						inst->setName(elementParam->Attribute("name"));
						inst->setValue(paramval);

						item->addInstance(inst);
					}

					if(node->NextSibling()) node = node->NextSibling();
					else break;
				}
			}
			node = nodeContent;
			if(nodeContent->NextSibling()) node = nodeContent->NextSibling();
			else break;
		}

		time(&curtime);
		schd = item->getSchedule();

		if (schd > 0) {
			schd = (curtime-(curtime%schd)) + schd;
		} else {
			schd = curtime;
		}
		item->setCollectTime(schd);

		schd = item->getEventSchedule();

		if (schd > 0) {
			schd = (curtime-(curtime%schd)) + schd;
		} else {
			schd = curtime;
		}

		item->setEventCollectTime(curtime);
		m_itemQ->enqueue(item, deleteCItem);
		// find next item.
		if(nodeItem->NextSibling()) node = nodeItem->NextSibling();
		else break;
	}
}

CItem *CAgentConfigVar::getItem(std::string code)
{
	CItem *item=NULL;
	elem *e=NULL;

	lock();
	for(e=m_itemQ->frontNode();e!=NULL;e=m_itemQ->getNext(e)){
		if(((CItem *)e->d)->getCode() == code){
			item = (CItem *)e->d;
			break;
		}
	}
	unlock();
	return item;
}

void CAgentConfigVar::addItem(CItem *item)
{
	
	lock();
	m_itemQ->enqueue(item, deleteCItem);
	makeXmlElement(item);
	m_doc->FirstChild("config")->LinkEndChild(makeXmlElement(item));
	unloadXMLConfigVar();
	unlock();
}

void CAgentConfigVar::setItem(CItem *item)
{
	lock();
	removeDocItem(item->getCode());
	m_doc->FirstChild("config")->LinkEndChild(makeXmlElement(item));
	unloadXMLConfigVar();
	unlock();
}

void CAgentConfigVar::delItem(std::string code)
{
	CItem *item=NULL;
	elem *e=NULL;

	lock();
	for(e=m_itemQ->frontNode();e!=NULL;e=m_itemQ->getNext(e)){
		if(code==((CItem *)e->d)->getCode()){
			item = (CItem *)m_itemQ->deleteNode(e);
			delete item;
			break;
		}
	}
	removeDocItem(code);
	unloadXMLConfigVar();
	unlock();
}

CQueue *CAgentConfigVar::getItemQ()
{
	return m_itemQ;
}

void CAgentConfigVar::unloadXMLConfigVar()
{
	m_doc->SaveFile();
}

TiXmlElement *CAgentConfigVar::makeXmlElement(CItem *item)
{
	CQueue *instQ = item->getInstanceQ();
	CQueue *condQ = item->getConditionQ();
	TiXmlElement *element=new TiXmlElement("item");

	linkEndChild(item->getCode(), element, "code");
	linkEndChild(item->getName(), element, "name");
	linkEndChild(item->getSchedule(), element, "schedule");
	linkEndChild(item->getEventSchedule(), element, "eschedule");
	linkEndChild(item->getEnable(), element, "enable");
	linkEndChild(item->getMethod(), element, "method");

	// add instance to item.
	if(instQ->isEmpty() == false){
		elem *e=NULL;
		TiXmlElement *nodeInstances = new TiXmlElement("instances");
		for(e=instQ->frontNode(); e!=NULL; e=instQ->getNext(e)){
			CItemInstance* _inst = (CItemInstance *)e->d;
			TiXmlElement *nodeInstance = new TiXmlElement("instance");
			TiXmlText *text = new TiXmlText(_inst->getValue().c_str());
			nodeInstance->SetAttribute("name", _inst->getName().c_str());
			nodeInstance->LinkEndChild(text);
			nodeInstances->LinkEndChild(nodeInstance);
		}
		element->LinkEndChild(nodeInstances);
	}

	// add condition to item.
	if(condQ->isEmpty() == false){
		TiXmlElement *nodeConditions = new TiXmlElement("conditions");
		elem *e=NULL;
		for(e=condQ->frontNode(); e!=NULL; e=condQ->getNext(e)){
			char temp[256];
			CItemCondition *_cond = (CItemCondition *)e->d;
			TiXmlElement *nodeCondition = new TiXmlElement("condition");
			TiXmlText *text = new TiXmlText(_cond->getCondition().c_str());

			memset(temp, 0x00, sizeof(temp));
			sprintf(temp, "%d", _cond->getIndex());
			nodeCondition->SetAttribute("id", temp);
			nodeCondition->SetAttribute("instance", _cond->getInstanceName().c_str());
			memset(temp, 0x00, sizeof(temp));
			sprintf(temp, "%d", _cond->getElement());
			nodeCondition->SetAttribute("element", temp);
			nodeCondition->SetAttribute("level", _cond->getSeverity().c_str());

			nodeCondition->LinkEndChild(text);
			nodeConditions->LinkEndChild(nodeCondition);
		}
		element->LinkEndChild(nodeConditions);
	}

	return element;
}

void CAgentConfigVar::linkEndChild(unsigned long l, TiXmlElement *elem, const char *name)
{
	char buf[32];

	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "%d", l);
	std::string str = buf;
	linkEndChild(str, elem, name);
}

void CAgentConfigVar::linkEndChild(std::string str, TiXmlElement *elem, const char *name)
{
	TiXmlElement *_elem = new TiXmlElement(name);
	TiXmlText *_text = new TiXmlText(str.c_str());
	_elem->LinkEndChild(_text);
	elem->LinkEndChild(_elem);
}

void CAgentConfigVar::removeDocItem(std::string code)
{
	TiXmlNode *nodeCode=NULL, *nodeValue=NULL;
	TiXmlNode *nodeConfig = m_doc->FirstChild("config");
	TiXmlNode *nodeItem = nodeConfig->FirstChild();

	while(!nodeConfig->NoChildren()){
		nodeCode = nodeItem->FirstChild();
		nodeValue = nodeCode->FirstChild();
		if(code==nodeValue->Value()){
			nodeConfig->RemoveChild(nodeItem);
			break;
		}

		if(nodeItem->NextSibling()) nodeItem = nodeItem->NextSibling();
	}
}

bool CAgentConfigVar::setUserInfo(std::string uid, std::string passwd, std::string accessip)
{
	TiXmlElement *elementParam=NULL;
	elementParam = m_doc->FirstChild("userinfo")->ToElement();	

	lock();
	if(uid != getUserid()) return false;

	if(accessip != ""){
		setAccessIP((char *)accessip.c_str());
	}

	if(passwd != ""){
		char en_passwd[128];

		memset(en_passwd, 0x00, sizeof(en_passwd));
		MD5::encode((char *)passwd.c_str(), en_passwd);
		setPasswd(en_passwd);
	}

	elementParam->SetAttribute("password", getPasswd().c_str());
	elementParam->SetAttribute("accessip", getAccessIP().c_str());
	unloadXMLConfigVar();
	unlock();

	return true;
}

void CAgentConfigVar::lock()
{
	pthread_mutex_lock(&m_lock);
}

void CAgentConfigVar::unlock()
{
	pthread_mutex_unlock(&m_lock);
}
