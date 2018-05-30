#include <string.h>
#include <stdio.h>
#include <assert.h>
#include <errno.h>

#include <string>

using namespace std;

#include <pthread.h>
#include "PthMutex.h"

PthMutex::PthMutex()
{
    this->mutex_init_flag = false;

    int r = pthread_mutex_init(&this->mutex_, NULL);
    if (r != 0) {
        fprintf(stderr, "(%s,%d) pthread_mutex_init() failed\n",
            __FILE__, __LINE__);
        return;
    }

    pthread_mutex_lock(&this->mutex_);
    this->mutex_init_flag = true;
    pthread_mutex_unlock(&this->mutex_);
}

PthMutex::~PthMutex()
{
    if (this->mutex_init_flag) {
        pthread_mutex_unlock(&this->mutex_);
        pthread_mutex_destroy(&this->mutex_);
        this->mutex_init_flag = false;
    }
}

void PthMutex::acquire()
{
    if (! this->mutex_init_flag) {
        fprintf(stderr, "(%s,%d) pthread_mutex_init() failed\n",
            __FILE__, __LINE__);
        return;
    }

  try_again:

    int r = pthread_mutex_lock(&this->mutex_);

    if (r != 0) {
        fprintf(stderr, "(%s,%d) pthread_mutex_lock() failed: %d\n",
            __FILE__, __LINE__, r);
    }

    if (r == EAGAIN) {
        goto try_again;
    }
}

void PthMutex::release()
{
    if (! this->mutex_init_flag) {
        fprintf(stderr, "(%s,%d) pthread_mutex_init() failed\n",
            __FILE__, __LINE__);
        return;
    }

    int r = pthread_mutex_unlock(&this->mutex_);

    if (r != 0) {
        fprintf(stderr, "(%s,%d) pthread_mutex_lock() failed: %d\n",
            __FILE__, __LINE__, r);
    }
}

static PthMutex *s_mutex = NULL; // global single mutex for guard
static pthread_mutex_t m;

PthGuard::PthGuard()
{
    // Double-Check Pattern
    if (s_mutex == NULL) {
        int r = pthread_mutex_init(&m, NULL);
        if (r != 0) {
            fprintf(stderr, "(%s,%d) pthread_mutex_init() failed: %d\n",
                __FILE__, __LINE__, r);
            this->mutex_init_flag = false;
            return;
        }

        r = pthread_mutex_lock(&m);
        if (r != 0) {
            fprintf(stderr, "(%s,%d) pthread_mutex_lock() failed: %d\n",
                __FILE__, __LINE__, r);
            this->mutex_init_flag = false;
            return;
        }

        if (s_mutex == NULL) {
            s_mutex = new PthMutex();
            assert(s_mutex != NULL);
        }
        r = pthread_mutex_unlock(&m);
        if (r != 0) {
            fprintf(stderr, "(%s,%d) pthread_mutex_lock() failed: %d\n",
                __FILE__, __LINE__, r);
            this->mutex_init_flag = false;
            return;
        }
    }

    s_mutex->acquire();
    this->mutex_ = s_mutex;
    this->mutex_init_flag = true;
}

PthGuard::PthGuard(PthMutex &mutex)
{
    this->mutex_init_flag = false;

    if (mutex.mutex_init_flag) {
        mutex.acquire();
        this->mutex_ = &mutex;
        this->mutex_init_flag = true;
    } else {
        fprintf(stderr, "(%s,%d) PthGuard::PthGuard(): not initialized\n",
                __FILE__, __LINE__);
        this->mutex_init_flag = false;
        return;
    }
}

PthGuard::~PthGuard()
{
    if (this->mutex_init_flag) {
        if (this->mutex_ != NULL) {
            this->mutex_->release();
            this->mutex_init_flag = false;
        } else {
            fprintf(stderr, "(%s,%d) PthGuard::PthGuard(): not initialized\n",
                __FILE__, __LINE__);
            this->mutex_init_flag = false;
            return;
        }
    } else {
        fprintf(stderr, "(%s,%d) PthGuard::PthGuard(): not initialized\n",
                __FILE__, __LINE__);
        this->mutex_init_flag = false;
        return;
    }
}

PthCondition::PthCondition()
{
    pthread_mutex_init(&this->mutex_, NULL);
    pthread_cond_init(&this->cond_, NULL);
}

PthCondition::~PthCondition()
{
    pthread_cond_broadcast(&this->cond_); // signal==notify(1)
    pthread_mutex_unlock(&this->mutex_);

    pthread_cond_destroy(&this->cond_);
    pthread_mutex_destroy(&this->mutex_);
}

int PthCondition::wait()
{
    pthread_mutex_lock(&this->mutex_);
    pthread_cond_wait(&this->cond_, &this->mutex_);
    pthread_mutex_unlock(&this->mutex_);

    return 1;
}

int PthCondition::notify()
{
    pthread_cond_broadcast(&this->cond_); // signal() == notify(0)
    return 1;
}


#ifdef PTHMUTEX_TEST

#include "PthTask.h"

#define YIELD() PthTask::usleep(1)

class MyGlobal
{
  public:
    static int count_;

  public:
    static void increment() // 1만 증가시킴.
    {
      PthGuard guard;  // 여기서 lock을 해 줘야 함.

      { // critical section begin
        int prev = count_;           YIELD(); // thread switching 일어나게 함

        count_ += 2;                 YIELD(); // thread switching 일어나게 함

        if ((count_ - prev) == 2) {
            count_ -= 1;             YIELD(); // thread switching 일어나게 함
        }
      } // critical section end
    }

    static int get_count()
    {
      return count_;
    }
};

int MyGlobal::count_ = 0;

class MyThread: public PthTask 
{
  public:
    int MAX;

  public:
    MyThread(int max) { this->MAX = max; }

    void run()
    {
      for (int i = 0; i < this->MAX; i++) {
          MyGlobal::increment();
      }
    }
};

void test_0()
{
    printf("test_0() - "); fflush(stdout);

    int THR_SIZ = 5;
    int MAX = 10;

    MyThread *p[THR_SIZ];
    for (int i = 0; i < THR_SIZ; i++) {
        p[i] = new MyThread(MAX);
        p[i]->auto_delete = true;
        p[i]->start();
    }

    printf("."); fflush(stdout);

    while (PthTask::activeCount() > 0) {
        PthTask::usleep(1);
    }

    assert(MyGlobal::get_count() == (MAX * THR_SIZ));

    printf("ok.\n");
}

PthCondition cond;

class MyT1: public PthTask {
  public:
    void run()
    {
        printf("MyT1.wait()..."); fflush(stdout);
        cond.wait();
        printf("MyT1:sleep(1)..."); fflush(stdout);
        PthTask::sleep(1);
        printf("MyT1.notify()..."); fflush(stdout);
        cond.notify();
        printf("MyT1.exit()..."); fflush(stdout);
    }
};

class MyT2: public PthTask
{
  public:
    void run()
    {
        printf("MyT2:sleep(1)..."); fflush(stdout);
        PthTask::sleep(1);
        printf("MyT2.notify()..."); fflush(stdout);
        cond.notify();

      {
        PthGuard gx;
        printf("MyT2.wait()..."); fflush(stdout);
      }

        cond.wait();
        printf("MyT2.exit()..."); fflush(stdout);
     }
};

void test_1()
{
    printf("test_1() - ");
    MyT1 *t1 = new MyT1(); t1->auto_delete = true; t1->start();
    MyT2 *t2 = new MyT2(); t2->auto_delete = true; t2->start();

    while (PthTask::activeCount() > 0) { PthTask::usleep(10); }

    printf("ok.\n");
}

void test_2()
{
    printf("test_1() - ");

    for (int i = 0; i < 100; i++) {
        MyT1 *t1 = new MyT1(); t1->auto_delete = true; t1->start();
        MyT2 *t2 = new MyT2(); t2->auto_delete = true; t2->start();
    }

    while (PthTask::activeCount() > 0) { PthTask::usleep(10); }

    printf("ok.\n");
}

int main()
{
    test_0();
    test_1();
    test_2();
    return 0;
}

#endif // PTHMUTEX_TEST
