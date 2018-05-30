#ifndef __PthMutex_h__
#define __PthMutex_h__

#include <pthread.h>

class PthMutex
{
  public:
    bool mutex_init_flag;
    pthread_mutex_t mutex_;
    
  public:
    PthMutex();
    ~PthMutex();

  public:
    void acquire();
    void release();

  public:
    inline void lock() { this->acquire(); }
    inline void unlock() { this->release(); }
};

class PthGuard
{
  public:
    bool mutex_init_flag;
    PthMutex *mutex_;

  public:
    PthGuard();
    PthGuard(PthMutex &mutex);
    ~PthGuard();
}; 

class PthCondition
{
  public:
    pthread_cond_t cond_;
    pthread_mutex_t mutex_;

  public:
    PthCondition();
    ~PthCondition();

  public:
    int wait();
    int notify();
};


// http://www.joinc.co.kr/modules.php?name=News&file=article&sid=118#AEN111

#endif // __PthMutex_h__
