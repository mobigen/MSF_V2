#ifndef __PthServer_h__
#define __PthServer_h__

#include <stdlib.h>
#include <unistd.h>

#include <vector>
#include <algorithm>

using namespace std;

// #include "MSocket.h"

#include "PthTask.h"
#include "PthSocket.h"

#ifndef MSocket
#define MSocket PthSocket
#endif

class MultiProc
{
  private:
    vector<pid_t> *children;

  public:
    pid_t pid;

  private:
    int fork_delay;      // fork를 한번 하고, 새로운 fork하기 전까지의 주기
    int check_period;    // child proc 가 살았는지를 체크하는 주기
    int max_children;    // 동시에 있을 수 있는 프로세스 갯수

  public:
	int heartbeat_time;  // child process가 아무런 작업을 하지 않고
						 // 멈춰 있는 경우, 최대한 죽이지 않고,
						 // 참아줄 수 있는 시간
    string heartbeat_key; // children/monitoring parent 사이에 
						  // 서로 heartbeat를 교환할 키


  public:
    void set_check_period(int check_period);
    void set_fork_delay(int fork_delay);
    void set_max_children(int max_children);
	void set_heartbeat(const string &key, int time);


  public:
    MultiProc();

    virtual ~MultiProc();

  public:
    virtual void before_loop();
    virtual void init_child();
    virtual void main_service();

  public:
    void start();
};

class PthServer: public MultiProc
{
  public:
    PthSocket *listen_sock;

    int port;                  // 대기 포트번호

    int max_service_per_child; // 한 프로세스 내에서, 몇 개의 서비스를
                               // 처리한 후에 자살할 것인가... ( <= 0이면 무한!)

    int max_threads;           // 한 프로세스 내의 최대 동시 스레드 수
                               // ( <= 0)이면 무제한

  public:
    PthServer();
    ~PthServer();

  public:
    inline void set_max_service_per_child(int max_service_per_child)
    {
        this->max_service_per_child = max_service_per_child;
    }

    inline void set_max_threads(int max_threads)
    {
        this->max_threads = max_threads;
    }

    inline void set_port(int port)
    {
        this->port = port;
    }

  private:
    void before_loop();
    void main_service();

  public:
    virtual void service(MSocket *sock);

    // void start()도 쓸 수 있음.
};

#endif // __PthServer_h__
