
#include "CProtocolProcessor.h"


void CProtocolProcessor::process(char *block)
{
	char *pcmd=NULL;
	if((pcmd = parse(block))==NULL){
		time_t polltime;
		time(&polltime);

		CMessageFormatter cmf;
		cmf.setPollTime(polltime);
		cmf.setType(TYPE_PASSIVE);
		cmf.setCommand(block);
		cmf.setTitle("syntax error\n");
		getEnvVar()->getRespQ()->enqueue(cmf.makeMessage(), NULL);
		return;

	}else{
		execute(pcmd);	
		free(pcmd);
	}
}

char * CProtocolProcessor::parse(char *block)
{
	char *ptrcmd=NULL;

	if((ptrcmd=m_reg->getMatchedString(block))!=NULL){
		if(parseCommand(ptrcmd)==false){ free(ptrcmd); return NULL; }
		return ptrcmd;
	}else
		return NULL;
}

bool CProtocolProcessor::parseCommand(char *ptrcmd)
{
	int i=0, n=0, len;
	char *p=NULL, *q=NULL;
	char sdata[30][1024], temp[128];

	if(strncmp(ptrcmd, "COL", 3)==0){
		m_cmd.opcode = OPCODE_COL;
	}else if(strncmp(ptrcmd, "COLINST", 7)==0){
		m_cmd.opcode = OPCODE_COLINST;
	}else if(strncmp(ptrcmd, "GETINST", 7)==0){
		m_cmd.opcode = OPCODE_GETINST;
	}else if(strncmp(ptrcmd, "SETINST", 7)==0){
		m_cmd.opcode = OPCODE_SETINST;
	}else if(strncmp(ptrcmd, "ADDINST", 7)==0){
		m_cmd.opcode = OPCODE_ADDINST;
	}else if(strncmp(ptrcmd, "DELINST", 7)==0){
		m_cmd.opcode = OPCODE_DELINST;
	}else if(strncmp(ptrcmd, "GETCOND", 7)==0){
		m_cmd.opcode = OPCODE_GETCOND;
	}else if(strncmp(ptrcmd, "SETCOND", 7)==0){
		m_cmd.opcode = OPCODE_SETCOND;
	}else if(strncmp(ptrcmd, "ADDCOND", 7)==0){
		m_cmd.opcode = OPCODE_ADDCOND;
	}else if(strncmp(ptrcmd, "DELCOND", 7)==0){
		m_cmd.opcode = OPCODE_DELCOND;
	}else if(strncmp(ptrcmd, "GET", 3)==0){
		m_cmd.opcode = OPCODE_GET;
	}else if(strncmp(ptrcmd, "SET", 3)==0){
		m_cmd.opcode = OPCODE_SET;
	}

	if((p = (char *)strchr(ptrcmd, ':'))==NULL) return false;
	p++;
	memset(sdata, 0x00, 30*1024);
	n = hrsplit(p, ",", sdata);
	if(n==0) return false;

	p = (char *)strchr(sdata[0], '=');
	p++;
	m_cmd.itemcode = p; // item code

	for(i=1;i<n;i++){
		memset(temp, 0x00, sizeof(temp));
		if((q = (char *)strchr(sdata[i], '='))==NULL) return false;
		len = strlen(sdata[i])-strlen(q);
		strncpy(temp, sdata[i], len);
		q++;
		m_cmd.attr[i-1].name = temp;
		m_cmd.attr[i-1].value = q;
	}

	m_cmd.attr_num = n-1;

	return true;
}

void CProtocolProcessor::execute(char *pcmd)
{
	switch(m_cmd.opcode){
		case OPCODE_COL:
			execCOL(pcmd);
			break;
		case OPCODE_GET:
			execGET(pcmd);
			break;
		case OPCODE_SET:
			execSET(pcmd);
			break;
		case OPCODE_GETINST:
			execGETINST(pcmd);
			break;
		case OPCODE_SETINST:
			execSETINST(pcmd);
			break;
		case OPCODE_ADDINST:
			execADDINST(pcmd);
			break;
		case OPCODE_DELINST:
			execDELINST(pcmd);
			break;
		case OPCODE_GETCOND:
			execGETCOND(pcmd);
			break;
		case OPCODE_SETCOND:
			execSETCOND(pcmd);
			break;
		case OPCODE_ADDCOND:
			execADDCOND(pcmd);
			break;
		case OPCODE_DELCOND:
			execDELCOND(pcmd);
			break;
		default:
			return;
	}
	return;
}

void CProtocolProcessor::execCOL(char *pcmd)
{
	int i=0,n=0;
	char sdata[32][1024];
	time_t polltime;
	CPolicyItem *pollitem=NULL;
	CItem *item=NULL;

	time(&polltime);
	if((item=getEnvVar()->getAgentConfigVar()->getItem(m_cmd.itemcode)) == NULL){
		char buf[128];
		CMessageFormatter fmt;

		memset(buf, 0x00, sizeof(buf));
		sprintf(buf, "CODE : [%s] is unregistered!!\n", m_cmd.itemcode.c_str());
		fmt.setTitle(buf);
		fmt.setType(TYPE_PASSIVE);
		fmt.setPollTime(polltime);
		fmt.setCommand(pcmd);
		getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
		return;
	}

	pollitem = new CPolicyItem();
	for(i=0;i<m_cmd.attr_num;i++){
		if(m_cmd.attr[i].name=="INST"){
			memset(sdata, 0x00, 32*1024);
			n = hrsplit((char *)m_cmd.attr[i].value.c_str(), "^", sdata);
			break;
		}
	}

	for(i=0;i<n;i++){
		pollitem->getInstQ()->enqueue(strdup(sdata[i]), NULL);
	}

	pollitem->setItem(item);
	pollitem->setPollTime(polltime);
	pollitem->setPollType(TYPE_PASSIVE);
	pollitem->setCommand(pcmd);

	getEnvVar()->getPolicyQ()->enqueue(pollitem, NULL);
	return;
}

void CProtocolProcessor::execGET(char *pcmd)
{
	time_t polltime;
	CItem *item=NULL;
	char buf[512];
	CMessageFormatter fmt;

	time(&polltime);
	if((item=getEnvVar()->getAgentConfigVar()->getItem(m_cmd.itemcode)) == NULL){

		memset(buf, 0x00, sizeof(buf));
		sprintf(buf, "CODE : [%s] is unregistered!!\n", m_cmd.itemcode.c_str());
		fmt.setTitle(buf);
		fmt.setType(TYPE_PASSIVE);
		fmt.setPollTime(polltime);
		fmt.setCommand(pcmd);
		getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
		return;
	}

	fmt.setItem(item);
	fmt.setTitle("CODE	SCHEDULE	ESCHEDULE	ENABLE	METHOD	DESCRIPTION\n");
	fmt.setType(TYPE_PASSIVE);
	fmt.setPollTime(polltime);
	fmt.setCommand(pcmd);
	memset(buf, 0x00, sizeof(buf));
	sprintf(buf, "%s	%d	%d	%s	%s	%s\n",
		item->getCode().c_str(), item->getSchedule(), item->getEventSchedule(),
		item->getEnable().c_str(), item->getMethod().c_str(),
		item->getName().c_str());
		fmt.addMessage(strdup(buf));

	getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
	return;
}

void CProtocolProcessor::execSET(char *pcmd)
{
	time_t polltime;
	CItem *item=NULL;
	char buf[256];
	int n, i;
	CMessageFormatter fmt;
	time(&polltime);


	if(m_cmd.itemcode == SC_ITEM_CODE_USERINFO){
		setUserInfo(pcmd);
		return;
	}

	if((item=getEnvVar()->getAgentConfigVar()->getItem(m_cmd.itemcode)) == NULL){

		memset(buf, 0x00, sizeof(buf));
		sprintf(buf, "CODE : [%s] is unregistered!!\n", m_cmd.itemcode.c_str());
		fmt.setTitle(buf);
		fmt.setType(TYPE_PASSIVE);
		fmt.setPollTime(polltime);
		fmt.setCommand(pcmd);
		getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
		return;
	}

	for(i=0;i<m_cmd.attr_num;i++){
		if(m_cmd.attr[i].name == SC_ITEM_ATTR_SCHEDULE){
			item->setSchedule(atoi(m_cmd.attr[i].value.c_str()));
		}else if(m_cmd.attr[i].name == SC_ITEM_ATTR_EVENT_SCHEDULE){
			item->setEventSchedule(atoi(m_cmd.attr[i].value.c_str()));
		}else if(m_cmd.attr[i].name == SC_ITEM_ATTR_ENABLE){
			item->setEnable(m_cmd.attr[i].value);
		}else if(m_cmd.attr[i].name == SC_ITEM_ATTR_METHOD){
			item->setMethod(m_cmd.attr[i].value);
		}
	}

	item->printItem();
	getEnvVar()->getAgentConfigVar()->setItem(item);
	execGET(pcmd);

	return;
}

void CProtocolProcessor::execGETINST(char *pcmd)
{
	time_t polltime;
	CItem *item=NULL;
	CItemInstance *inst=NULL;
	CQueue *instQ=NULL;
	elem *e=NULL;
	char buf[256];
	int n, i;
	CMessageFormatter fmt;
	time(&polltime);
	if((item=getEnvVar()->getAgentConfigVar()->getItem(m_cmd.itemcode)) == NULL){

		memset(buf, 0x00, sizeof(buf));
		sprintf(buf, "CODE : [%s] is unregistered!!\n", m_cmd.itemcode.c_str());
		fmt.setTitle(buf);
		fmt.setType(TYPE_PASSIVE);
		fmt.setPollTime(polltime);
		fmt.setCommand(pcmd);
		getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
		return;
	}

	instQ = item->getInstanceQ();
	fmt.setItem(item);
	fmt.setTitle("NAME	VALUE\n");
	fmt.setType(TYPE_PASSIVE);
	fmt.setPollTime(polltime);
	fmt.setCommand(pcmd);
	for(e=instQ->frontNode();e!=NULL;e=instQ->getNext(e)){
		inst = (CItemInstance *)e->d;
		memset(buf, 0x00, sizeof(buf));
		sprintf(buf, "%s	%s\n", inst->getName().c_str(), inst->getValue().c_str());
		fmt.addMessage(strdup(buf));
	}

	getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
	return;
}

void CProtocolProcessor::execSETINST(char *pcmd)
{
	return;
}

void CProtocolProcessor::execADDINST(char *pcmd)
{
	time_t polltime;
	CItem *item=NULL;
	CItemInstance *inst=NULL;
	CQueue *instQ=NULL;
	elem *e=NULL;
	char arinstname[32][1024];
	int n, i;

	time(&polltime);
	if((item=getEnvVar()->getAgentConfigVar()->getItem(m_cmd.itemcode)) == NULL){
		char buf[128];
		CMessageFormatter fmt;

		memset(buf, 0x00, sizeof(buf));
		sprintf(buf, "CODE : [%s] is unregistered!!\n", m_cmd.itemcode.c_str());
		fmt.setTitle(buf);
		fmt.setType(TYPE_PASSIVE);
		fmt.setPollTime(polltime);
		fmt.setCommand(pcmd);
		getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
		return;
	}

	if(m_cmd.attr_num != 1 || m_cmd.attr[0].name != "INST"){
		char buf[128];
		CMessageFormatter fmt;

		memset(buf, 0x00, sizeof(buf));
		strcpy(buf, "syntax error!!\n");
		fmt.setTitle(buf);
		fmt.setType(TYPE_PASSIVE);
		fmt.setPollTime(polltime);
		fmt.setCommand(pcmd);
		getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
		return;
	}
	memset(arinstname, 0x00, sizeof(arinstname));
	n = hrsplit((char *)m_cmd.attr[0].value.c_str(), "^", arinstname);

	instQ = item->getInstanceQ();

	for(i=0;i<n;i++){
		bool isFind=false;
		for(e=instQ->frontNode();e!=NULL;e=instQ->getNext(e)){
			inst = (CItemInstance *)e->d;
			if(inst->getValue() == arinstname[i]){
				char buf[128];
				CMessageFormatter fmt;
		
				memset(buf, 0x00, sizeof(buf));
				sprintf(buf, "INSTANCE : [%s] already registered!!\n", arinstname[i]);
				fmt.setTitle(buf);
				fmt.setType(TYPE_PASSIVE);
				fmt.setPollTime(polltime);
				fmt.setCommand(pcmd);
				getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
				isFind=true;
				break;
			}
		}

		if(isFind==false){
			CItemInstance *_inst = new CItemInstance();
			_inst->setName(arinstname[i]);
			_inst->setValue(arinstname[i]);
			instQ->enqueue(_inst, deleteCItemInstance);
		}
	}

	getEnvVar()->getAgentConfigVar()->setItem(item);
	execGETINST(pcmd);
	return;
}

void CProtocolProcessor::execDELINST(char *pcmd)
{
	time_t polltime;
	CItem *item=NULL;
	CItemInstance *inst=NULL;
	CQueue *instQ=NULL;
	elem *e=NULL;
	char arinstname[32][1024];
	int n, i;

	time(&polltime);
	if((item=getEnvVar()->getAgentConfigVar()->getItem(m_cmd.itemcode)) == NULL){
		char buf[128];
		CMessageFormatter fmt;

		memset(buf, 0x00, sizeof(buf));
		sprintf(buf, "CODE : [%s] is unregistered!!\n", m_cmd.itemcode.c_str());
		fmt.setTitle(buf);
		fmt.setType(TYPE_PASSIVE);
		fmt.setPollTime(polltime);
		fmt.setCommand(pcmd);
		getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
		return;
	}

	if(m_cmd.attr_num != 1 || m_cmd.attr[0].name != "INST"){
		char buf[128];
		CMessageFormatter fmt;

		memset(buf, 0x00, sizeof(buf));
		strcpy(buf, "syntax error!!\n");
		fmt.setTitle(buf);
		fmt.setType(TYPE_PASSIVE);
		fmt.setPollTime(polltime);
		fmt.setCommand(pcmd);
		getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
		return;
	}

	instQ = item->getInstanceQ();

	if(m_cmd.attr[0].value == "ALL") instQ->removeAll();
	else{
		memset(arinstname, 0x00, sizeof(arinstname));
		n = hrsplit((char *)m_cmd.attr[0].value.c_str(), "^", arinstname);
	
	
		for(i=0;i<n;i++){
			for(e=instQ->frontNode();e!=NULL;e=instQ->getNext(e)){
				inst = (CItemInstance *)e->d;
				if(inst->getValue() == arinstname[i]){
					instQ->removeNode(e);
					break;
				}
			}
		}
	
	}

	getEnvVar()->getAgentConfigVar()->setItem(item);
	execGETINST(pcmd);
	return;
}

void CProtocolProcessor::execGETCOND(char *pcmd)
{
	time_t polltime;
	CItem *item=NULL;
	CItemCondition *cond=NULL;
	CQueue *condQ=NULL;
	elem *e=NULL;
	char buf[1024], arinstname[32][1024];
	int n, i;
	CMessageFormatter fmt;

	time(&polltime);
	if((item=getEnvVar()->getAgentConfigVar()->getItem(m_cmd.itemcode)) == NULL){
		memset(buf, 0x00, sizeof(buf));
		sprintf(buf, "CODE : [%s] is unregistered!!\n", m_cmd.itemcode.c_str());
		fmt.setTitle(buf);
		fmt.setType(TYPE_PASSIVE);
		fmt.setPollTime(polltime);
		fmt.setCommand(pcmd);
		getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
		return;
	}

	fmt.setItem(item);
	fmt.setTitle("COMMAND	ID	Element	Instance	Condition	Level\n");
	fmt.setPollTime(polltime);
	fmt.setCommand(pcmd);
	fmt.setType(TYPE_PASSIVE);

	condQ = item->getConditionQ();
	for(e=condQ->frontNode();e!=NULL;e=condQ->getNext(e))
	{
		cond = (CItemCondition *)e->d;
		memset(buf, 0x00, sizeof(buf));
		sprintf(buf, "GETCOND	%d	%d	%s	%s	%s\n",
			cond->getIndex(), cond->getElement(),
			cond->getInstanceName().c_str(),
			cond->getCondition().c_str(), cond->getSeverity().c_str());
		fmt.addMessage(strdup(buf));
	}
	
	getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
	return;
}

void CProtocolProcessor::execSETCOND(char *pcmd)
{
	time_t polltime;
	CItem *item=NULL;
	CItemCondition *cond=NULL;
	CQueue *condQ=NULL;
	elem *e=NULL;
	char buf[1024];
	int condid, i=0;
	bool isFind=false;
	CMessageFormatter fmt;

	time(&polltime);
	if((item=getEnvVar()->getAgentConfigVar()->getItem(m_cmd.itemcode)) == NULL){
		memset(buf, 0x00, sizeof(buf));
		sprintf(buf, "CODE : [%s] is unregistered!!\n", m_cmd.itemcode.c_str());
		fmt.setTitle(buf);
		fmt.setType(TYPE_PASSIVE);
		fmt.setPollTime(polltime);
		fmt.setCommand(pcmd);
		getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
		return;
	}

	if(m_cmd.attr_num < 1 || m_cmd.attr[0].name != "CONDID"){
		memset(buf, 0x00, sizeof(buf));
		strcpy(buf, "syntax error!!\n");
		fmt.setTitle(buf);
		fmt.setType(TYPE_PASSIVE);
		fmt.setPollTime(polltime);
		fmt.setCommand(pcmd);
		getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
		return;
	}

	condQ = item->getConditionQ();
	condid = atoi(m_cmd.attr[0].value.c_str());
	for(e=condQ->frontNode();e!=NULL;e=condQ->getNext(e)){
		cond = (CItemCondition *)e->d;
		if(condid == cond->getIndex()){
			for(i=0;i<m_cmd.attr_num;i++){
				if(m_cmd.attr[i].name == SC_ITEM_ATTR_ELEMENT){
					cond->setElement((unsigned int) atoi(m_cmd.attr[i].value.c_str()));
				}else if(m_cmd.attr[i].name == SC_ITEM_ATTR_CONDITION){
					cond->setCondition(m_cmd.attr[i].value);
				}else if(m_cmd.attr[i].name == SC_ITEM_ATTR_LEVEL){
					cond->setSeverity(m_cmd.attr[i].value);
				}else if(m_cmd.attr[i].name == SC_ITEM_ATTR_INSTANCE){
					cond->setInstanceName(m_cmd.attr[i].value);
				}
			}
			cond->setChange(); // condition를 reset한다.
			isFind = true;
			break;
		}
	}

	if(isFind!=true){
		memset(buf, 0x00, sizeof(buf));
		sprintf(buf, "unregistered CONDID : %d !!\n", condid);
		fmt.setTitle(buf);
		fmt.setType(TYPE_PASSIVE);
		fmt.setPollTime(polltime);
		fmt.setCommand(pcmd);
		getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
		return;
	}

	getEnvVar()->getAgentConfigVar()->setItem(item);
	execGETCOND(pcmd);

	return;
}

void CProtocolProcessor::execADDCOND(char *pcmd)
{
	time_t polltime;
	CItem *item=NULL;
	CItemCondition *cond=NULL;
	CQueue *condQ=NULL;
	elem *e=NULL;
	char buf[1024], arinstname[32][1024];
	int n, i;
	CMessageFormatter fmt;

	time(&polltime);
	if((item=getEnvVar()->getAgentConfigVar()->getItem(m_cmd.itemcode)) == NULL){
		memset(buf, 0x00, sizeof(buf));
		sprintf(buf, "CODE : [%s] is unregistered!!\n", m_cmd.itemcode.c_str());
		fmt.setTitle(buf);
		fmt.setType(TYPE_PASSIVE);
		fmt.setPollTime(polltime);
		fmt.setCommand(pcmd);
		getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
		return;
	}

	condQ = item->getConditionQ();
	cond = new CItemCondition();
	cond->setIndex((unsigned int )(condQ->size()+1));
	for(i=0;i<m_cmd.attr_num;i++){
		if(m_cmd.attr[i].name == SC_ITEM_ATTR_ELEMENT){
			cond->setElement((unsigned int) atoi(m_cmd.attr[i].value.c_str()));
		}else if(m_cmd.attr[i].name == SC_ITEM_ATTR_CONDITION){
			cond->setCondition(m_cmd.attr[i].value);
		}else if(m_cmd.attr[i].name == SC_ITEM_ATTR_LEVEL){
			cond->setSeverity(m_cmd.attr[i].value);
		}else if(m_cmd.attr[i].name == SC_ITEM_ATTR_INSTANCE){
			cond->setInstanceName(m_cmd.attr[i].value);
		}
	}

	condQ->enqueue(cond, deleteCItemCondition);

	getEnvVar()->getAgentConfigVar()->setItem(item);
	execGETCOND(pcmd);

	return;
}

void CProtocolProcessor::execDELCOND(char *pcmd)
{
	time_t polltime;
	CItem *item=NULL;
	CItemCondition *cond=NULL;
	CQueue *condQ=NULL;
	elem *e=NULL;
	char buf[1024];
	int condid;
	bool isFind=false;
	CMessageFormatter fmt;

	time(&polltime);
	if((item=getEnvVar()->getAgentConfigVar()->getItem(m_cmd.itemcode)) == NULL){
		memset(buf, 0x00, sizeof(buf));
		sprintf(buf, "CODE : [%s] is unregistered!!\n", m_cmd.itemcode.c_str());
		fmt.setTitle(buf);
		fmt.setType(TYPE_PASSIVE);
		fmt.setPollTime(polltime);
		fmt.setCommand(pcmd);
		getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
		return;
	}

	if(m_cmd.attr_num < 1 || m_cmd.attr[0].name != "CONDID"){
		memset(buf, 0x00, sizeof(buf));
		strcpy(buf, "syntax error!!\n");
		fmt.setTitle(buf);
		fmt.setType(TYPE_PASSIVE);
		fmt.setPollTime(polltime);
		fmt.setCommand(pcmd);
		getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
		return;
	}

	condQ = item->getConditionQ();
	condid = atoi(m_cmd.attr[0].value.c_str());
	for(e=condQ->frontNode();e!=NULL;e=condQ->getNext(e)){
		cond = (CItemCondition *)e->d;
		if(condid == cond->getIndex()){
			condQ->removeNode(e);
			isFind = true;
			break;
		}
	}

	if(isFind!=true){
		memset(buf, 0x00, sizeof(buf));
		sprintf(buf, "unregistered CONDID : %d !!\n", condid);
		fmt.setTitle(buf);
		fmt.setType(TYPE_PASSIVE);
		fmt.setPollTime(polltime);
		fmt.setCommand(pcmd);
		getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);
		return;
	}

	getEnvVar()->getAgentConfigVar()->setItem(item);
	execGETCOND(pcmd);

	return;
}

void CProtocolProcessor::setUserInfo(char *pcmd)
{
	int i=0;
	char buf[1024];
	std::string uid="";
	std::string passwd="";
	std::string accessip="";
	CMessageFormatter fmt;
	CItem item;
	time_t polltime;
	time(&polltime);

	for(i=0;i<m_cmd.attr_num;i++){
		if(m_cmd.attr[i].name == SC_ITEM_ATTR_USERID){
			uid = m_cmd.attr[i].value;
		}else if(m_cmd.attr[i].name == SC_ITEM_ATTR_PASSWD){
			passwd = m_cmd.attr[i].value;
		}else if(m_cmd.attr[i].name == SC_ITEM_ATTR_ACCESSIP){
			accessip = m_cmd.attr[i].value;
		}
	}

	item.setCode(SC_ITEM_CODE_USERINFO);
	item.setName("SMS Agent 계정 설정 및 조회.");
	fmt.setItem(&item);
	fmt.setTitle("Access_IP\n");
	fmt.setType(TYPE_PASSIVE);
	fmt.setPollTime(polltime);
	fmt.setCommand(pcmd);

	if(getEnvVar()->getAgentConfigVar()->setUserInfo(uid, passwd, accessip)==true)
	{

		memset(buf, 0x00, sizeof(buf));
		sprintf(buf, "%s\n", getEnvVar()->getAgentConfigVar()->getAccessIP().c_str());
		fmt.addMessage(strdup(buf));
	}else{
		fmt.addMessage(strdup("Invalid USERID!\n"));
	}

	getEnvVar()->getRespQ()->enqueue(fmt.makeMessage(), NULL);

	return;
}
