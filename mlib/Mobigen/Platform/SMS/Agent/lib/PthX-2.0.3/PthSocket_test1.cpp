#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <assert.h>
#include <errno.h>
#include <ctype.h>

#include <sys/types.h>
#include <sys/wait.h>

#include "PthTask.h"
#include "PthSocket.h"

#ifndef DEBUG_PRINT
#  define DEBUG_PRINT printf("(%s,%d) ", __FILE__, __LINE__); printf
#endif // DEBUG_PRINT

class ServiceThread: public PthTask
{
  public:
    PthSocket *sock;

  public:
    ServiceThread(PthSocket *sock)
    {
        this->sock = sock;
    }

  public:
    void run()
    {
        char *welcome = "WELCOME\r\n";
        this->sock->write(welcome, strlen(welcome));
        while (1) {
            char buf[BUFSIZ];

            // int r = this->sock->readline(buf, 10);
            // printf("READ\n");
            int r = this->sock->readline(buf); // , 100);

            if (r < 0) {
                DEBUG_PRINT("timeout or socket_error\n");
                this->sock->close();
                break;
            } else if (r == 0) {
                DEBUG_PRINT("socket closed\n");
                this->sock->close();
                break;
            } else {
                for (int i = 0; i < r; i++) {
                    buf[i] = toupper(buf[i]);
                }

                this->sock->write(buf, r);

                if (strncmp(buf, "QUIT", 4) == 0) {
                    this->sock->close();
                    break;
                }
            }
        }

        delete this->sock;
    }
};

int main()
{
    PthSocket *server = new PthSocket(9993);

    if (server == NULL || server->error) {
        printf("new PthSocket(9993) failed\n");
        exit(0);
    }

    for (int i = 0; i < 3; i++) {
        if (fork() == 0) {
            while (1) {
                // printf("ACCEPT\n");
                PthSocket *client = server->accept(); // 50);
                if (client == NULL || client->error) {
                    PthTask::sleep(1);
                    DEBUG_PRINT("server->accept() failed, continue\n");
                    continue;
                }

                ServiceThread *child = new ServiceThread(client);
                child->start();
            }
            exit(0);
        }
    }

    wait(NULL);
}

