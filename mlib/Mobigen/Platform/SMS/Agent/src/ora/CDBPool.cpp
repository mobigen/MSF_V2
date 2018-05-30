
#include "CDBPool.h"


CDBPool::CDBPool()
{
	pthread_mutex_init(&m_mutex, NULL);
	m_pool = new CQueue();
}

CDBPool::~CDBPool()
{
	pthread_mutex_destroy(&m_mutex);
	delete m_pool;
}


void CDBPool::putSession(CDBSession *sess)
{
	pthread_mutex_lock(&m_mutex);
	m_pool->enqueue(sess, NULL);
	pthread_mutex_unlock(&m_mutex);
}

CDBSession *CDBPool::getSession(char *userid, char *passwd, char *sid)
{
	char uid[128];
	memset(uid, 0x00, sizeof(uid));
	sprintf(uid, "%s/%s@%s", userid, passwd, sid);
	return getSession(uid);
}

CDBSession *CDBPool::getSession(char *key)
{
	CDBSession *sess = NULL;
	elem *e=NULL;
	pthread_mutex_lock(&m_mutex);
	for(e=(elem *)m_pool->frontNode(); e != NULL && e->d!=NULL ; e=(elem *)m_pool->getNext(e)){
		char *skey=NULL;
		sess = (CDBSession *)e->d;
		skey = sess->getKey();
		if(strcmp(sess->getKey(), key)==0){
			return sess;
		}
	}
	pthread_mutex_unlock(&m_mutex);
	return NULL;
}

void CDBPool::returnSession(CDBSession *sess)
{
	pthread_mutex_unlock(&m_mutex);
}
