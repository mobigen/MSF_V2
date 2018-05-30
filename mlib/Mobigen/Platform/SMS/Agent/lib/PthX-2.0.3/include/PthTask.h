#ifndef __PthTask_h__
#define __PthTask_h__

#include <pthread.h>

class PthTask
{
  public:
    pthread_t tid;

  public:
    bool auto_delete;

  public:
    PthTask();
    virtual ~PthTask();

  public:
    void start();
    void join();

  public:
    virtual void run() = 0;
    void set_auto_delete(bool auto_delete); // auto-detached

  public:
    static void usleep(int micro_sec);
    static void sleep(int sec);
    static void yield();

    static int activeCount();
    static int aliveCount();

  public:
    static bool isAlive(PthTask *thr);

  public:
//    static int pth_init_flag;
    static int thr_self();
};

#endif // __PthTask_h__

