#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <assert.h>
#include <stdlib.h>
#include <errno.h>
#include <time.h>

#include <sys/types.h>
#include <sys/wait.h> // wait()

#include "PthTask.h"
#include "PthSocket.h"

int global_count = 0;

time_t start_time;

#ifndef DEBUG_PRINT
#  define DEBUG_PRINT printf("(%s,%d) ", __FILE__, __LINE__); printf
#endif // DEBUG_PRINT

char *ip_addr = NULL;
int port = 0;

class ClientThread: public PthTask
{
  public:
    void run()
    {
      restart:
        PthSocket *client_sock = new PthSocket(ip_addr, port);

        if (client_sock == NULL || client_sock->error) {
            DEBUG_PRINT("new PthSocket(ip, port) failed, %s\n",
                strerror(errno));

            if (client_sock != NULL) {
                 delete client_sock;
            }

            goto restart;

            return;
        }

        char welcome[BUFSIZ];
        client_sock->readline(welcome); // , 5);
        if (client_sock->isError()) {
            client_sock->close();
            delete client_sock;

            global_count++;
            DEBUG_PRINT("time: %d, global_count: %d, active:%d\n",
                 (int)(time(NULL) - start_time), global_count,
                 PthTask::activeCount());

            return;
        }

        bool broken = false;
        for (int i = 0; i < 2; i++) {
            char *line = "fkldsjfkldsajflkdsjfdslkfjaklfsjdaklfd\r\n";
            client_sock->write(line, strlen(line));
            if (client_sock->isError()) {
                broken = true;
                break;
            }

            char buf[BUFSIZ];
            client_sock->readline(buf); // , 10);
            if (client_sock->isError()) {
                broken = true;
                break;
            }

            // PthTask::yield();
        }

        if (! broken) {
            client_sock->write("quit\r\n", 6);
        }

        client_sock->close();
        delete client_sock;

        global_count++;

        if (global_count % 30 == 0) {
            DEBUG_PRINT("t:%d, global_count:%d, pid:%d, activeCount:%d\n",
                 (int)(time(NULL) - start_time),
                 global_count, (int)getpid(), PthTask::activeCount());
        }

      goto restart;
    }
};

class Pop3Thread: public PthTask
{
  public:
    void run()
    {
      restart:
        PthSocket *client_sock = new PthSocket(ip_addr, port);
                // , 5);

        if (client_sock == NULL || client_sock->error) {
            DEBUG_PRINT("new PthSocket(127.0.0.1, 9994) failed, %s\n",
                strerror(errno));

            if (client_sock != NULL) {
                 delete client_sock;
            }

            goto restart;

            return;
        }

        char welcome[BUFSIZ];
        client_sock->readline(welcome); // , 5);
        if (client_sock->isError()) {
            client_sock->close();
            delete client_sock;

            global_count++;
            DEBUG_PRINT("ERROR time: %d, global_count: %d, active:%d\n",
                 (int)(time(NULL) - start_time), global_count,
                 PthTask::activeCount());

            return;
        }

        char *user = "user fkdslaj\r\n";
        client_sock->write(user, strlen(user));
        if (client_sock->isError()) {
            client_sock->close();
            delete client_sock;

            global_count++;
            DEBUG_PRINT("ERROR time: %d, global_count: %d, active:%d\n",
                 (int)(time(NULL) - start_time), global_count,
                 PthTask::activeCount());

            return;
        }

      {
        char buf[BUFSIZ];
        client_sock->readline(buf); // , 10);
        if (client_sock->isError()) {
            client_sock->close();
            delete client_sock;

            global_count++;
            DEBUG_PRINT("ERROR time: %d, global_count: %d, active:%d\n",
                 (int)(time(NULL) - start_time), global_count,
                 PthTask::activeCount());

            return;
        }
      }

        char *pass = "pass fkdslaj\r\n";
        client_sock->write(pass, strlen(pass));
        if (client_sock->isError()) {
            client_sock->close();
            delete client_sock;

            global_count++;
            DEBUG_PRINT("ERROR time: %d, global_count: %d, active:%d\n",
                 (int)(time(NULL) - start_time), global_count,
                 PthTask::activeCount());

            return;
        }

      {
        char buf[BUFSIZ];
        client_sock->readline(buf); // , 10);
        if (client_sock->isError()) {
            client_sock->close();
            delete client_sock;

            global_count++;
            DEBUG_PRINT("ERROR time: %d, global_count: %d, active:%d\n",
                 (int)(time(NULL) - start_time), global_count,
                 PthTask::activeCount());

            return;
        }
      }

        char *retr = "retr fkdslaj\r\n";
        client_sock->write(retr, strlen(retr));
        if (client_sock->isError()) {
            client_sock->close();
            delete client_sock;

            global_count++;
            DEBUG_PRINT("ERROR time: %d, global_count: %d, active:%d\n",
                 (int)(time(NULL) - start_time), global_count,
                 PthTask::activeCount());

            return;
        }


        bool done = false;
        int count = 0;
        int size = 0;
        while (! done) {
            count++;
            char buf[BUFSIZ];
            int n = client_sock->readline(buf); // , 10);
            if (client_sock->isError()) {
                client_sock->close();
                delete client_sock;

                global_count++;
                DEBUG_PRINT("ERROR time:%d,global_cnt:%d,active:%d,cnt:%d\n",
                     (int)(time(NULL) - start_time), global_count,
                     PthTask::activeCount(), count);
    
                return;
            }

            size += n;

            if (strncmp(buf, ".\r\n", 3) == 0) {
                break;
            }
        }

        char *quit = "quit\r\n";
        client_sock->write(quit, strlen(quit));
        if (client_sock->isError()) {
            client_sock->close();
            delete client_sock;

            global_count++;
            DEBUG_PRINT("ERROR time: %d, global_count: %d, active:%d\n",
                 (int)(time(NULL) - start_time), global_count,
                 PthTask::activeCount());

            return;
        }

       
        client_sock->close();
        delete client_sock;

        global_count++;

        if (global_count % 3 == 0) {
            DEBUG_PRINT("OK t:%d,global_cnt:%d,pid:%d,activeCnt:%d,size:%d\n",
                 (int)(time(NULL) - start_time),
                 global_count, (int)getpid(), PthTask::activeCount(), size);
        }

       goto restart;
    }
};

int main(int argc, char *argv[])
{
    if (argc < 2) {
        printf("Usage: %s ipaddr port\n", argv[0]);
        exit(0);
    }

    ip_addr = argv[1];
    port = atoi(argv[2]);

    start_time = time(NULL);
    while (1) {

        if (PthTask::activeCount() < 30) {
            for (int i = 0; i < 100; i++) {
                // Pop3Thread *client = new Pop3Thread();
                ClientThread *client = new ClientThread();
                // client->set_auto_delete(true);
                client->start();
            }
        }

        PthTask::sleep(1);
    }

    return 0;
}

