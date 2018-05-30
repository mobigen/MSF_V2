#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <assert.h>
#include <stdlib.h>
#include <errno.h>
#include <time.h>

#include <sys/types.h>
#include <sys/wait.h> // wait()

#include "Pth.h++"
#include "PthSocket.h++"

int global_count = 0;

time_t start_time;

void write_anyway(PthSocket *client_sock, char *line)
{
  send_again:
    int r = client_sock->write(line, strlen(line));
    if (r <= 0 && errno == EAGAIN) {
        goto send_again;
    }
}

int read_anyway(PthSocket *client_sock, char *buf, int timeout)
{
  read_again:

    int r = client_sock->readline(buf, timeout);

    if (r <= 0 && errno == EAGAIN) {
        goto read_again;
    }

    return r;
}

class ClientThread: public Pth {
  public:
    void run()
    {
      restart:

        PthSocket *client_sock = new PthSocket("128.134.130.161", 25, 5);

        if (client_sock == NULL || client_sock->error) {
            printf("new PthSocket(128.134.130.161, 25) failed, %s\n",
                strerror(errno));

            goto restart;

            return;
        }

        char welcome[BUFSIZ];
        // int r = client_sock->readline(welcome, 5);
        int r = read_anyway(client_sock, welcome, 5);
        if (r <= 0) {
            client_sock->close();
            delete client_sock;

            global_count++;
            printf("global_count: %d, %d\n",
                 (int)(time(NULL) - start_time), global_count);

            return;
        } else {
            printf("%s", welcome);
        }

      {
        char *line = "HELO mobigen.com\r\n";
        // client_sock->write(line, strlen(line));
        write_anyway(client_sock, line);
 
        char buf[BUFSIZ];
        // int n = client_sock->readline(buf, 3);
        int n = read_anyway(client_sock, buf, 3);
        if (n <= 0) {
            client_sock->close();
            delete client_sock;

            global_count++;
            printf("global_count: %d, %d\n",
                 (int)(time(NULL) - start_time), global_count);

            return;
        } else {
            printf("%s", buf);
        }
      }

      {
        char *line = "MAIL FROM: nomota@mobigen.com\r\n";
        // client_sock->write(line, strlen(line));
        write_anyway(client_sock, line);
        char buf[BUFSIZ];
        // int n = client_sock->readline(buf, 3);
        int n = read_anyway(client_sock, buf, 3);
        if (n <= 0) {
            client_sock->close();
            delete client_sock;

            global_count++;
            printf("global_count: %d, %d\n",
                 (int)(time(NULL) - start_time), global_count);

            return;
        } else {
            printf("%s", buf);
        }
      }

      {
        char *line = "RCPT TO: hiongun@hanmir.com\r\n";
        // client_sock->write(line, strlen(line));
        write_anyway(client_sock, line);
        char buf[BUFSIZ];
        // int n = client_sock->readline(buf, 3);
        int n = read_anyway(client_sock, buf, 3);
        if (n <= 0) {
            client_sock->close();
            delete client_sock;

            global_count++;
            printf("global_count: %d, %d\n",
                 (int)(time(NULL) - start_time), global_count);

            return;
        } else {
            printf("%s", buf);
        }
      }

      {
        char *line = "DATA\r\n";
        // client_sock->write(line, strlen(line));
        write_anyway(client_sock, line);
        char buf[BUFSIZ];
        // int n = client_sock->readline(buf, 3);
        int n = read_anyway(client_sock, buf, 3);
        if (n <= 0) {
            client_sock->close();
            delete client_sock;

            global_count++;
            printf("global_count: %d, %d\n",
                 (int)(time(NULL) - start_time), global_count);

            return;
        } else {
            printf("%s", buf);
        }
      }

      {
        char *subject = "Subject: fdklsajfdkl fdkslfjl\r\n\r\n";
        // client_sock->write(subject, strlen(subject));
        write_anyway(client_sock, subject);

        for (int i = 0; i < 500; i++) {
            char *line = "fdsklajfklsajfdlksafjdlksafjdlksafjdlksafjdlk\r\n";

          send_again:
            int r = client_sock->write(line, strlen(line));
            if (r <= 0 && errno == EAGAIN) {
                goto send_again;
            }
        }

        char *dot = ".\r\n";
        // client_sock->write(dot, strlen(dot));
        write_anyway(client_sock, dot);

        char buf[BUFSIZ];
        // int n = client_sock->readline(buf, 3);
        int n = read_anyway(client_sock, buf, 3);
        if (n <= 0) {
            client_sock->close();
            delete client_sock;

            global_count++;
            printf("global_count: %d, %d\n",
                 (int)(time(NULL) - start_time), global_count);

            return;
        } else {
            printf("%s", buf);
        }
      }

      {
        char *line = "QUIT\r\n";
        // client_sock->write(line, strlen(line));
        write_anyway(client_sock, line);
      }

        client_sock->close();

        delete client_sock;

        global_count++;
        printf("global_count: %d, %d\n",
             (int)(time(NULL) - start_time), global_count);
    }
};

int main()
{
    for (int j = 0; j < 5; j++) {
        if (fork() == 0) {

          while (1) { 
            start_time = time(NULL);
            for (int i = 0; i < 50; i++) {
                ClientThread *client = new ClientThread();
                client->start();
            }

            while (Pth::activeCount() > 0) {
                Pth::sleep(1);
            }
          }

            exit(0);
        }
    }

    wait(NULL);

    return 0;
}

