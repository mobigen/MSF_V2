

#include "CQueue.h"

CQueue::CQueue()
{
	//type = t;
	isRemove = true;
	initialize();
}

CQueue::~CQueue()
{
	if(isRemove) removeAll();
	if(m_head != NULL) free(m_head);
	if(m_tail != NULL) free(m_tail);
	pthread_mutex_destroy(&m_lockkey);
}

void CQueue::initialize()
{
	m_count=0;
	m_writable = true;
	m_head = (elem *)malloc(sizeof(elem));
	m_tail = (elem *)malloc(sizeof(elem));
	m_head->next = m_tail;
	m_head->prev = m_head;
	m_head->d = NULL;
	m_tail->next = m_tail;
	m_tail->prev = m_head;
	m_tail->d = NULL;
	pthread_mutex_init(&m_lockkey, NULL);
}

elem *CQueue::frontNode()
{
	lock();
	elem *p=NULL;
	if(m_head->next == m_tail) p=NULL;
	else
		p = m_head->next;		
	unlock();
	return p;
}

elem *CQueue::getNext(elem *p)
{
	lock();
	elem* result = NULL;
	if(p->next == m_tail) result=NULL;
	else result = p->next;
	unlock();
	return result;
}

void CQueue::enqueue(void *d, void (*h)(void *))
{
	lock();
	elem *data=(elem*)malloc(sizeof(elem));
	data->d = d;
	data->handler = h;

	data->next = m_tail;
	data->prev = m_tail->prev;
	data->prev->next = data;
	m_tail->prev = data;
	
	m_count++;

	if(m_count>MAX_QUEUE_SIZE){
		//unlock();
		removeNode(m_head->next, true);
		//lock();
	}
	unlock();
}

void CQueue::push(void *d, void (*h)(void *))
{
	lock();
	elem *data=(elem*)malloc(sizeof(elem));
	data->d = d;
	data->handler = h;

	data->prev = m_head;
	data->next = m_head->next;
	data->next->prev = data;
	m_head->next = data;

	m_count++;

	if(m_count>MAX_QUEUE_SIZE){
		//unlock();
		removeNode(m_head->next, true);
		//lock();
	}
	unlock();
}

void *CQueue::dequeue()
{
	lock();
	void* result = NULL;
	if(m_count==0) result = NULL;
	else{
		elem *p=NULL, *t=NULL;
		//void *d=NULL;

		p = m_head->next;
		p->next->prev = m_head;
		p->prev->next = p->next;

		m_count--;
		result = p->d;
		free(p);
	}
	unlock();

	return result;
}

void CQueue::removeAll()
{
	lock();
	elem *p=NULL, *t=NULL;
	void *d=NULL;
	for(p = m_head->next; p!=m_tail;){
		t = p;
		p = p->next;
		d = t->d;

		if(t->handler != NULL) t->handler(d);
		else
			if(d) free(d);

		t->d = NULL;
		if(t) free(t);
		t = NULL;

	}
	m_head->next = m_tail;
	m_head->prev = m_head;
	m_tail->next = m_tail;
	m_tail->prev = m_head;
	m_count=0;
	unlock();
}

void *CQueue::deleteNode(elem *node)
{
	lock();
	elem *p=NULL, *t=NULL;
	void *d=NULL;
	p = node->prev;
	t = node->next;
	p->next = t;
	t->prev = p;
	d = node->d;
	free(node);
	m_count--;
	unlock();
	return d;
}

void CQueue::removeNode(elem *node,bool isLock)
{
	if (node == NULL) {
		return;
	}

	if (isLock == false) {
		lock();
	}

	elem *p=NULL, *t=NULL;
	void *d=NULL;
	p = node->prev;
	t = node->next;
	p->next = t;
	t->prev = p;
	d = node->d;

	if(node->handler != NULL) node->handler(d);
	else free(d);
		
	node->d = NULL;

	free(node); node = NULL;

	m_count--;

	if (isLock == false) {
		unlock();
	}
}

void *CQueue::getData()
{
	lock();
	void *d=NULL;
	if(m_count != 0) 
		d = m_head->next->d;
	unlock();
	return d;
}

void CQueue::lock()
{
	pthread_mutex_lock(&m_lockkey);
}

void CQueue::unlock()
{
	pthread_mutex_unlock(&m_lockkey);
}

int CQueue::size()
{
	lock();
	int result = m_count;
	unlock();
	return result;
}

bool CQueue::isEmpty()
{
	lock();
	bool result = false;
	if(m_count == 0) result = true;
	unlock();
	return result;
}

void CQueue::setWritable(bool b)
{
	lock();
	m_writable = b;
	unlock();
}

bool CQueue::isWritable()
{
	lock();
	bool result = m_writable;
	unlock();
	return result;
}

void CQueue::setName(std::string name)
{
	lock();
	m_name = name;
	unlock();
}

std::string CQueue::getName()
{
	lock();
	std::string result = m_name;
	unlock();
	return result;
}

void CQueue::setIsRemove(bool b)
{
	isRemove = b;
}


#ifdef __CQUEUE_TEST__

int main()
{

	CQueue c;

	while (true) {
	printf("......dddd.......\n");
	for (long i =0; i < MAX_QUEUE_SIZE ;i++) {
		c.enqueue((void*)strdup("test"), NULL);
	}
		printf("...............\n");

		sleep(5);
	}

	return 0;

}

#endif // __CQUEUE_TEST__
