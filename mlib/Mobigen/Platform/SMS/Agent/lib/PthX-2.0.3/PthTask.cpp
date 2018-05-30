
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/poll.h>
#include <errno.h>

#include <pthread.h>
#include <assert.h>

#include <vector>
#include <algorithm>
#include <map>
#include <string>

using namespace std;

#include "PthTask.h"

#ifndef DEBUG_PRINT
#  ifdef NDEBUG
#    define DEBUG_PRINT if (0) printf
#  else // NDEBUG
#    define DEBUG_PRINT printf("(%s,%d) ", __FILE__, __LINE__); printf
#  endif // NDEBUG
#endif // DEBUG_PRINT

// int PthTask::pth_init_flag = 0;

class ThreadVector: public std::vector<PthTask*> 
{
  private:
    typedef std::vector<PthTask*>::iterator Iter;
    pthread_mutex_t mutex;

  public:
    ThreadVector()
    {
//        mutex = PTHREAD_MUTEX_INITIALIZER;
        if (pthread_mutex_init(&this->mutex, NULL) != 0) {
            fprintf(stderr, "(%s,%d) PthTask pthread_mutex_init fail\n",
                 __FILE__, __LINE__);
        }

        pthread_mutex_lock(&this->mutex);
        // 2003.5.19 jch 추가
        this->clear();
        pthread_mutex_unlock(&this->mutex);
    }

    ~ThreadVector()
    {
        pthread_mutex_lock(&this->mutex);
        this->clear();
        pthread_mutex_unlock(&this->mutex);
    }

    inline void add(PthTask* thread)
    {
        assert(thread != NULL);

        pthread_mutex_lock(&this->mutex);

//      this->reserve(((this->size() / 10) + 1) * 10); // Memory Leak 제거
        this->push_back(thread);

        pthread_mutex_unlock(&this->mutex);
    }

    inline bool isAlive(PthTask *thread)
    {
        pthread_mutex_lock(&this->mutex);

        Iter item = std::find(this->begin(), this->end(), thread);
        bool r = (item != this->end());

        pthread_mutex_unlock(&this->mutex);

        return r;
    }

    inline void del(PthTask* thread)
    {
        assert(thread != NULL);

        pthread_mutex_lock(&this->mutex);

        Iter item = std::find(this->begin(), this->end(), thread);
        assert(item != this->end());
        if (item != this->end()) { this->erase(item); }

        pthread_mutex_unlock(&this->mutex);
    }

    inline int activeCount()
    {
        pthread_mutex_lock(&this->mutex);

        int r = this->size();

        pthread_mutex_unlock(&this->mutex);

        return r;
    }

    inline int aliveCount()
    {
        return this->activeCount();
    }

    inline int find(pthread_t tid)
    {
        int r = 0;

        pthread_mutex_lock(&this->mutex);
        for (int i = 0, n = this->size(); i < n; i++) {
            PthTask *thread = (*this)[i];
            if (thread->tid == tid) {
                r = i;
                break;
            }
        }
        pthread_mutex_unlock(&this->mutex);

        return r;
    }
};

ThreadVector ThreadList;

// static
int PthTask::thr_self()
{
    return ThreadList.find(pthread_self());
}

void thr_cleanup(void *pThis)
{
    assert(pThis != NULL);
    PthTask *This = (PthTask *) pThis;
    delete This; This = NULL;
}

void *thr_handler(void *pThis)
{
    assert(pThis != NULL);
    PthTask *This = (PthTask *) pThis;

    This->tid = pthread_self();

  if (This->tid == 0) {
     DEBUG_PRINT("error: %s\n", strerror(errno)); fflush(stdout);
     return NULL;
  }

    // pth_cleanup_push(thr_cleanup, pThis);

    // PthTask::start() 속에서 add(this_thread)를 미리 하고 들어왔음.
    // ThreadList.add(This);

    // DEBUG_PRINT("thr_handler()\n");

    This->run();

    // DEBUG_PRINT("thr_handler()\n");
    
  #if 1
    ThreadList.del(This);

    if (This->auto_delete) {
        delete This; This = NULL;
    }
  #endif

    //PthTask::usleep(1);
    //pthread_exit(NULL);

    return NULL;
}

void PthTask::set_auto_delete(bool auto_delete)
{
    this->auto_delete = auto_delete;
}

// static
void PthTask::usleep(int micro_sec)
{
    struct timeval tval;
    tval.tv_sec = micro_sec / 1000000;
    tval.tv_usec = micro_sec % 1000000;

    select(0, (fd_set *)NULL, (fd_set *)NULL, (fd_set *)NULL, &tval);
}

// static
void PthTask::sleep(int sec)
{
    struct timeval tval;

    tval.tv_sec = sec;
    tval.tv_usec = 0;

    select(0, (fd_set *)NULL, (fd_set *)NULL, (fd_set *)NULL, &tval);
}

// static
void PthTask::yield()
{
    // do nothing
}

// static 
bool PthTask::isAlive(PthTask *thread)
{
    assert(thread != NULL);
    return ThreadList.isAlive(thread);
}

PthTask::PthTask()
{
//    if (! PthTask::pth_init_flag) {
//        PthTask::pth_init_flag = 1;
//    }

    this->tid = 0;
    this->auto_delete = false;
}

PthTask::~PthTask()
{

}

void PthTask::join()
{
    void *exit_value;

    pthread_join(this->tid, &exit_value);
}

void PthTask::start()
{
    pthread_attr_t attr;
    pthread_attr_init(&attr);
    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);

 // int count = 0;
 try_again:

    ThreadList.add(this); // spawn()하기 전에 미리 ThreadList에 넣어야 한다.

    pthread_t dummy;
    int n = pthread_create(&dummy, &attr, thr_handler, (void*)this);

    if (n != 0) {
        this->tid = 0;

        // pthread_create() 실패시 오류 처리.


     // DEBUG_PRINT("Start ERROR(pthread_create return %d, %s)\n", n,
     //     strerror(errno)); fflush(stdout);
     // assert(0);

        ThreadList.del(this);
        PthTask::usleep(1);

        // if (count++ == 10) {
            // printf(".(%d)", PthTask::activeCount()); fflush(stdout);
        // }

        goto try_again;
    }

    pthread_attr_destroy(&attr);

    // FIXME: 2004/04/21 메모리 reclaim을 원활하게 하기 위해서 추가됨
    // FIXME: 여기에 usleep(1)이 들어가면, 상대적으로
    //        매우 느려지는 현상이 있음.
    // PthTask::usleep(1); // 2004/06/16굳이 여기서 usleep()할 필요가 없어 보임
}

int PthTask::activeCount()
{
    return ThreadList.activeCount();
}

int PthTask::aliveCount()
{
    return ThreadList.aliveCount();
}

#ifdef PTH_TEST

int global_run_count = 0;
int global_del_count = 0;

class MyThread: public PthTask
{
   public:
     void run();

   public:
     ~MyThread()
     {
// printf("."); fflush(stdout);
         global_del_count++;
     }
};

void MyThread::run()
{
    map<string, string> m;

    m["fdksljfdsaaaaaaaafadsssssssssssssssssssssssssssssssssssssssssssssss"] =
       "==fasfdfdsajjkfsajflfasdlkfslfdasjlkafljkflkflfdkjlfdkjlfkjfldkjfdjlk"
       "==fasfdfdsajjkfsajflfasdlkfslfdasjlkafljkflkflfdkjlfdkjlfkjfldkjfdjlk"
       "==fasfdfdsajjkfsajflfasdlkfslfdasjlkafljkflkflfdkjlfdkjlfkjfldkjfdjlk"
       "==fasfdfdsajjkfsajflfasdlkfslfdasjlkafljkflkflfdkjlfdkjlfkjfldkjfdjlk"
       "==fasfdfdsajjkfsajflfasdlkfslfdasjlkafljkflkflfdkjlfdkjlfkjfldkjfdjlk"
       "==fasfdfdsajjkfsajflfasdlkfslfdasjlkafljkflkflfdkjlfdkjlfkjfldkjfdjlk";

  // PthTask::usleep(1);
     m.clear();
     PthTask::usleep(1);
 /*
    if (rand()%2 == 0) {
        PthTask::yield();
    }

    if (rand()%2 == 0) {
        PthTask::yield();
        PthTask::sleep((rand()%2) + 1);
    }

    if (rand()%2 == 0) {
        PthTask::yield();
    }

    global_run_count++;
 */
}

int __main()
{
    time_t t0 = time(NULL);
    while (1) {
        if (PthTask::activeCount() < 100) {
            for (int i = 0; i < (100 - PthTask::activeCount()); i++) {
                MyThread *thr = new MyThread();
                // thr->set_auto_delete(true);
                thr->start();
            }
        }
        time_t t1 = time(NULL);
        printf("active: %d, alive:%d, run:%d, del:%d, thrput:%3.2f\n", 
          PthTask::activeCount(), PthTask::aliveCount(),
          global_run_count, global_del_count,
            (float)global_del_count/(float)(t1-t0));

        if (global_run_count > 1000) {
            break;
        }

        PthTask::sleep(1);
    }

    while (PthTask::activeCount() > 0) {
        PthTask::sleep(1);
    }

    return 0;
}

int main()
{
    for (int i = 0; i < 50000; i++) {
     // while (PthTask::activeCount() >= 500) {
     //     // printf("*{%d}", PthTask::activeCount()); fflush(stdout);
     //     PthTask::usleep(1);
     // }
        
        MyThread *thr = new MyThread();
        thr->set_auto_delete(true);
        thr->start(); // thr을 delete하면 안됨. --> auto_delete 됨
    }

    // PthTask::sleep(1);
    // DEBUG_PRINT("pth::activeCount() %d\n", PthTask::activeCount());

    while (1) {
        printf("."); fflush(stdout);
        PthTask::usleep(500000);
    }

    return 0;
}

#endif // PTH_TEST

