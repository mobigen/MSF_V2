
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include <string>
#include <map>

using namespace std;

#include <pthread.h>
#include "StrUtil.h"
#include "PthTask.h"

pthread_mutex_t mutex;

void init_guard()
{
    pthread_mutex_init(&mutex, NULL);
}

class MyShared
{
  public:
    map<string,string> m;

  public:
    string FETCH(const string &key)
    {
        pthread_mutex_lock(&mutex);

        string a = this->m[key];

        pthread_mutex_unlock(&mutex);

        return a;
    }

    void STORE(const string &key, const string &val)
    {
        pthread_mutex_lock(&mutex);

        this->m[key] = val;

        pthread_mutex_unlock(&mutex);
    }
};

MyShared H;

class MyThread: public PthTask 
{
  public:
    void run()
    {
        for (int i = 0, n = 100; i < n; i++) {
            string key = "key";
            string val = "val";

            H.STORE(key, val);

            string y = H.FETCH(key);
                   y = H.FETCH(key);
        }
    }
};

int main(int argc, char *argv[])
{
    int n_thr = 10;

    if (argc < 2) {
        printf("Usage: %s -n_thr=%d\n", argv[0], n_thr);
        exit(0);
    }

    init_guard();

    for (int i = 0; i < argc; i++) {
        if (strncmp(argv[i], "-n_thr=", 7) == 0) { n_thr = atoi(&argv[i][7]); }
    }

    for (int i = 0; i < n_thr; i++) {
        MyThread *thr = new MyThread();
        thr->auto_delete = true;
        thr->start();
    }

    while (PthTask::activeCount() > 0) {
        PthTask::sleep(1);
    }
}

