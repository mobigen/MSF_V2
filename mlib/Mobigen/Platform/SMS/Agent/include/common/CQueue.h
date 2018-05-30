
#ifndef __CQUEUE_H__
#define __CQUEUE_H__ 

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <pthread.h>
#include <errno.h>
#include <unistd.h>
#include <string>

#define MAX_QUEUE_SIZE	10000

/**
 *	리스큐의 노드 정보를 저장하는 구조체.
 */
typedef struct __elem__
{
	void *d;
	void (*handler)(void *);
	struct __elem__ *next;
	struct __elem__ *prev;
}elem;


//!	각종 데이터를 저장하기 위한 리스트 큐 클래스.
/**
 *	SMS Agent가 기동하면서 필요한 각종 데이터를 저장하고, 관리하는 리스트 큐 클래스.
 */
class CQueue
{
	private:
		bool m_writable;			/**< 큐가 쓰기 가능한지 여부 */
		int m_count;				/**< 큐에 저장된 데이터 개수 */
		std::string m_name;			/**< 큐 이름 */
		elem *m_head;				/**< 데이터 큐의 head */
		elem *m_tail;				/**< 데이터 큐의 tail */
		pthread_mutex_t m_lockkey;	/**< 데이터 큐의 동기화 키 */
		int type;					/**< 데이터 큐 타입 */
		/** 큐 잠금 메쏘드 */
		void lock();
		/** 큐 잠금 해지 메쏘드 */
		void unlock();
		/** 큐의 삭제 가능 여부 */
		bool isRemove;
	
	public:
		/** 생성자 */
		CQueue();
		/**
		 *	생성자.
		 *	@param 큐 이름.
		 */
		CQueue(std::string);
		/** 소멸자 */
		virtual ~CQueue();
		/**
		 *	큐 초기화 메쏘드.
		 */
		void initialize();
		/**
		 *	큐에 대한 쓰기 가능 여부을 조회하는 메쏘드.
		 *	@return true : 쓰기 가능, false : 쓰기 불가능.
		 */
		bool isWritable();
		/**
		 *	큐의 첫번째 노드를 조회하는 메쏘드.
		 *	@return 첫번째 노드 포인터.
		 */
		elem *frontNode();
		/**
		 *	주어진 노드의 다음 노드 정보를 조회하는 메쏘드.
		 *	@param 노드 포인터.
		 *	@return 노드 포일터.
		 */
		elem *getNext(elem *e);
		/**
		 *	큐의 쓰기 가능 여부를 설정하는 메쏘드.
		 *	@param true : 쓰기 가능, false : 쓰기 불가능.
		 */
		void setWritable(bool b);
		/**
		 *	큐에 존재하는 모든 노드 및 데이터를 삭제하는 메쏘드.
		 */
		void removeAll();
		/**
		 *	큐에 데이터를 주가하는 메쏘드. FIFO처럼 가장 끝 노드에 추가한다.
		 *	@param 데이터 포인터.
		 *	@param 데이터를 삭제할 때 호출할 함수 포인터.
		 */
		void enqueue(void *d, void (*h)(void *));
		/**
		 *	큐에 데이터를 주가하는 메쏘드. 스택처럼 가장 처음 노드에 추가한다.
		 *	@param 데이터 포인터.
		 *	@param 데이터를 삭제할 때 호출할 함수 포인터.
		 */
		void push(void *d, void (*h)(void *));
		/**
		 *	큐에서 가장 처음에 들어온 데이터를 가져오는 메쏘드.
		 *	@param data pointer.
		 */
		void *dequeue();
		//void *front();
		/**
		 *	큐에서 특정 노드를 삭제하는 메쏘드. 노드 정보는 삭제되고 실 데이터 정보는 반환된다.
		 *	반환된 데이터는 반환받은 개체가 메모리에서 삭제해주어야 한다.
		 *	@param 삭제하고자 하는 노드.
		 *	@return 삭제된 노드가 저장하고 있던 데이터.
		 */
		void *deleteNode(elem *e);
		/**
		 *	큐에서 특정 노드 및 데이터 정보를 삭제하는 메쏘드.
		 *	@param 삭제하고자 하는 노드.
		 */
		void removeNode(elem *e, bool isLock=false);
		/**
		 *	첫번째 노드의 데이터 정보를 가져오는 메쏘드. 현재 의미없음.
		 */
		void *getData();
		/**
		 *	큐의 저장된 데이터 개수를 조회하는 메쏘드.
		 *	@return data count.
		 */
		int size();
		/**
		 *	큐가 비어 있는지 여부를 판단하는 메쏘드.
		 *	@return true if queue is empty, else return false.
		 */
		bool isEmpty();
		/**
		 *	큐 이름을 조회하는 메쏘드.
		 *	@return queue name.
		 */
		std::string getName();
		/**
		 *	큐 이름을 설정하는 메쏘드.
		 *	@param queue name.
		 */
		void setName(std::string name);
		/**
		 *	큐의 데이터 삭제 여부를 설정하는 메쏘드. 현재 의미 없음.
		 */
		void setIsRemove(bool);
};

#endif /* __CQUEUE_H__ */
