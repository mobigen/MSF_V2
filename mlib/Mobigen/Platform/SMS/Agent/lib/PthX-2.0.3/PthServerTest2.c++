
#include "PthServer.h++"

class MyService: public PthServer {
  public:
    void service(PthSocket *sock)
    {
        char *welcome = "OK Welcome MyService\r\n";
        sock->write(welcome, strlen(welcome));

        while (1) {
            char buf[BUFSIZ]; // buf크기는 반드시 BUFSIZ이어야 함.
            int r = sock->readline(buf, 10); // timeout = 10 seconds

            if (r < 0) { printf("SOCK ERROR or TIMEOUT\r\n"); break; }

            if (r == 0) { printf("SOCK CLOSED\r\n"); break; }

            char *ok = "OK ";

            sock->write(ok, strlen(ok));
            sock->write(buf, strlen(buf));

            if (strncmp(buf, "QUIT", 4) == 0 || strncmp(buf, "quit", 4) == 0) {
                break;
            }
        }

        sock->close();

        delete sock;
    }
};

int main()
{
    MyService server;

    server.setPort(9995);
    server.setMaxChildren(1);
    server.setMaxThreads(100);

    server.start();
}

