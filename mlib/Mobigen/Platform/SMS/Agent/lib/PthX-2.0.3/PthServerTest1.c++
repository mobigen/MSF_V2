#include "PthServer.h++"

int main()
{
    // 아무런 상속 없이 그냥 쓰면, Echo 서버가 생성된다.
    PthServer *server = new PthServer();

    server->setPort(9994);

    // server->setMaxChildren(2);
    // server->setMaxThreads(2);

    server->start();

    delete server;

    return 0;
}

