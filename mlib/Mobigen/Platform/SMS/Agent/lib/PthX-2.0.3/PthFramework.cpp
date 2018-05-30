#include <stdio.h>
#include <string.h>
#include <cassert>

#include "PthTask.h"
#include "PthSocket.h"
#include "PthServer.h"

using namespace std;

#ifndef DEBUG_PRINT
#  ifdef NDEBUG
#    define DEBUG_PRINT if (0) printf
#  else // NDEBUG
#    define DEBUG_PRINT printf("(%s,%d) ", __FILE__, __LINE__); printf
#  endif // NDEBUG
#endif // DEBUG_PRINT

extern void main_setup(); // 전체 프로그램 시작 전에 호출할 코드
extern void main_teardown(); // 전체 프로그램 종료후 호출할 코드

extern void setup();    // 스레드 서비스 시작하기 전에 호출할 코드
extern void teardown(); // thread 서비스 끝내고 나서 호출할 코드

extern int service_main(int sock_fd);

class MyGenericServer: public PthServer
{
  public:
    void service(PthSocket *sock)
    {
        assert(sock != NULL);
        setup();

        service_main(sock->getSockFd());

        teardown();
    }
};

int _max_service_per_child = 0;

void read_svc_conf(int &port, int &num_thread)
{
    extern int _process_num;

    FILE *fp = fopen("./svc.conf", "r");
    if (fp != NULL) {
        char buf[BUFSIZ];
        while (fgets(buf, BUFSIZ, fp) != NULL) {
            if (buf[0] == '#') { continue; }

            // -----------------------------------------------------------
            // 2003/12/27 _process_num 변수의 값을, svc.conf 로부터 읽어
            //            들이도록 한다. process_num 0 이면 single process
            //            모델이고, process_num 1 이면, 모니터링 프로세스가
            //            하나 더 뜨는 모델이다.
            // -----------------------------------------------------------
            if (strncmp(buf, "process_num ", 12) == 0) {
                sscanf(&buf[12], "%d", &_process_num);
                continue;
            }

            // -----------------------------------------------------------
            // 2004/01/08 max_service_per_chiled 개념 도입
            //            특정 process가 몇회 이상 서비스를 하고 나서 
            //            죽도록 한다.  메모리 리크 문제를 해결하기 위해서
            //            또는 서비스 블락 문제를 해결하기 위해서
            //            process_num == 0일 때는 동작하지 않는다.
            //            max_service_per_child == 0일 때는 무한히 반복한다.
            // -----------------------------------------------------------
            if (strncmp(buf, "max_service_per_child ", 22) == 0) {
                sscanf(&buf[22], "%d", &_max_service_per_child);
                continue;
            }

            char *p = strstr(buf, "-p ");
            if (p == NULL) {
                continue;
            }
            assert(p != NULL);
            port = ::atoi(p+3);

            char *n = strstr(buf, "-n ");
            if (n == NULL) {
                continue;
            }
            assert(n != NULL);
            num_thread = ::atoi(n+3);
        }
        fclose(fp);
    } else {
        DEBUG_PRINT("fopen(svc.conf, 'r') failed\n");
    }
}

int main()
{
DEBUG_PRINT("main_setup()\n");
    main_setup();

    MyGenericServer server;

    int port, num_thread;

DEBUG_PRINT("read_svc_conf()\n");
    read_svc_conf(port, num_thread);

DEBUG_PRINT("port: %d\n", port);
    server.set_port(port);

    extern int _process_num;
DEBUG_PRINT("process_num: %d\n", _process_num);
    server.set_max_children(_process_num);

DEBUG_PRINT("set_max_thread(%d)\n", num_thread);
    server.set_max_threads(num_thread);

DEBUG_PRINT("set_max_service_per_child(%d)\n", _max_service_per_child);
    if (_process_num == 0) {
        DEBUG_PRINT("process_num == 0: _max_service_per_child must be zero\n");
        _max_service_per_child = 0;
    }
    server.set_max_service_per_child(_max_service_per_child);

DEBUG_PRINT("server.start()\n");
    server.start();

DEBUG_PRINT("main_teardown()\n");
    main_teardown();

    return 0;
}


#ifdef PTH_FRAMEWORK_TEST

// global number to be specified
int _process_num = 2;

void main_setup()
{
    DEBUG_PRINT("main_setup() called\n");
}

void main_teardown()
{
    DEBUG_PRINT("main_teardown() called\n");
}

void setup()
{
    DEBUG_PRINT("setup() called\n");
}

void teardown()
{
    DEBUG_PRINT("teardown() called\n");
}

int service_main(int sock_fd)
{
    MSocket sock;
    sock.set_sockfd(sock_fd);

    string hello = "hello service_main()\r\n";
    sock.write(hello.c_str(), hello.size());
    if (sock.isError()) {
        DEBUG_PRINT("isError()\n");
        sock.close();
        return 0;
    }

    while (1)
    {
        string line;
        sock.read_line(line);
        if (sock.isError()) {
            DEBUG_PRINT("error\r\n");
            break;
        }

        if (strncasecmp(line.c_str(), "QUIT", 4) == 0) {
            break;
        }

        line = "OK " + line;
        sock.write(line.c_str(), line.size());
        if (sock.isError()) {
            DEBUG_PRINT("error\n");
            break;
        }
    }

    sock.close();
    return 1;
}

#endif // PTH_FRAMEWORK_TEST
