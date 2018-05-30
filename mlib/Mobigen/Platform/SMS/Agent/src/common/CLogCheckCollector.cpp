

#include "CLogCheckCollector.h"

using namespace std;

CLogCheckCollector::CLogCheckCollector()
{
}

CLogCheckCollector::~CLogCheckCollector()
{
}

void CLogCheckCollector::collect()
{
	checkFmtInstance(); /* 처음 기동시 파일 정보를 로딩한다. */

	/* 과거 이후 정보 수집 시작. */
	collectLog();

	/* 인스턴스 설정값 편경(파일 정보 변경시 파일 정보 재로딩 */
	setFmtInstance();

	/* 파일 정보가 변경됐을 경우에 새로운 정보 수집 */
	collectLog();

	setFmtInstance();
}

void CLogCheckCollector::checkFmtInstance()
{
	CQueue *instq = getPolicyItem()->getItem()->getInstanceQ();
	elem *e=NULL;

	for(e=instq->frontNode();e!=NULL;e=instq->getNext(e))
	{
		CItemInstance *inst = (CItemInstance *)e->d;
		if(inst->getDataQ()->isEmpty()==true){ /* start monitoring log file */
			st_loginst *loginst = (st_loginst *)malloc(sizeof(st_loginst));
			memset(loginst, 0x00, sizeof(loginst));
			strcpy(loginst->instance, inst->getValue().c_str());
			setLogFileInfo(loginst, true);
			inst->getDataQ()->enqueue(loginst, NULL);
		}
	}
}

void CLogCheckCollector::setFmtInstance()
{
	CQueue *instq = getPolicyItem()->getItem()->getInstanceQ();
	elem *e=NULL;

	for(e=instq->frontNode();e!=NULL;e=instq->getNext(e))
	{
		CItemInstance *inst = (CItemInstance *)e->d;
		setLogFileInfo((st_loginst *)inst->getDataQ()->frontNode()->d, false);
	}
}

void CLogCheckCollector::setLogFileInfo(st_loginst *loginst, bool b)
{
	time_t curtime;
	struct tm *ptm=NULL;
	char path[256];

	time(&curtime);
	ptm = localtime(&curtime);

	memset(path, 0x00, sizeof(path));
	strftime(path, sizeof(path)-1, loginst->instance, ptm);
	stat(path, &(loginst->sbuf));

	if(strcmp(path, loginst->fmt_instance)!=0 && b==false){
		loginst->sbuf.st_size = 0;
	}

	strcpy(loginst->fmt_instance, path);

	return;
}

void CLogCheckCollector::collectLog()
{
	CQueue *instq = getPolicyItem()->getItem()->getInstanceQ();
	elem *e=NULL;

	for(e=instq->frontNode();e!=NULL;e=instq->getNext(e))
	{
		CItemInstance *inst = (CItemInstance *)e->d;
		collectLogInstance((st_loginst *)inst->getDataQ()->frontNode()->d);
	}
}

void CLogCheckCollector::collectLogInstance(st_loginst *loginst)
{
	FILE *fp=NULL;
	char buf[1024];

	if((fp = fopen(loginst->fmt_instance, "r"))==NULL) return;
	
	if(fseek(fp, loginst->sbuf.st_size, SEEK_CUR)!=0){
		fclose(fp);
		return;
	}

	memset(buf, 0x00, sizeof(buf));
	while(fgets(buf, sizeof(buf)-1, fp)){
		checkCondition(loginst, buf);
		memset(buf, 0x00, sizeof(buf));
	}

	fclose(fp);
	return;
}

void CLogCheckCollector::checkCondition(st_loginst *loginst, char *log)
{
	CQueue *condq = getPolicyItem()->getItem()->getConditionQ();
	elem *e=NULL;

	for(e=condq->frontNode();e!=NULL;e=condq->getNext(e)){
		CItemCondition *cond = (CItemCondition *)e->d;
		if(	cond->getInstanceName()=="ALL" || 
			cond->getInstanceName()==loginst->instance ){

			if(cond->isOverThreshold(log)==true){
				sendEvent(cond, loginst, log);
			}
		}
	}
}

void CLogCheckCollector::sendEvent(CItemCondition *cond, st_loginst *loginst, char *log)
{
	char tab=0x09;
	CMessageFormatter msgfmt;
	char msg[1024];
	time_t curtime; time(&curtime);

	msgfmt.setItem(m_pollitem->getItem());
	msgfmt.setPollTime(curtime);
	msgfmt.setType(TYPE_EVENT);
	msgfmt.setItemCondition(cond);
	msgfmt.setEventStatus(true);

	memset(msg, 0x00, sizeof(msg));
	sprintf(msg, "Instance%cMessages\n", tab);
	msgfmt.setTitle(msg);

	memset(msg, 0x00, sizeof(msg));
	sprintf(msg, "%s%c%s\n", loginst->fmt_instance, tab, log);
	msgfmt.addMessage(strdup(msg));

	m_envvar->getEventQ()->enqueue(msgfmt.makeMessage(), NULL);

	return;
}

void CLogCheckCollector::makeMessage()
{
}

