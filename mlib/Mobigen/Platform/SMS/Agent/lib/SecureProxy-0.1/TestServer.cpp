#include <string>
#include <stdio.h>
using namespace std;

#include "StrUtil.h"
#include "PthTask.h"
#include "SecureProxy.h"

int main(int argc, char *argv[])
{
    if (argc < 4) {
        printf("Usage: %s secure_listen_port text_ip:text_port shared_key\n",
            argv[0]);
        exit(0);
    }

    int s_port = atoi(argv[1]);
    vector<string> ip_port = StrUtil::split(argv[2], ":", 2);
    string t_ip = ip_port[0];
    int t_port = StrUtil::string2int(ip_port[1]);
    string shared_key = argv[3];
    

    SecureProxyServer *s_proxy_server =
         new SecureProxyServer(s_port, t_ip, t_port, shared_key);
    s_proxy_server->set_auto_delete(true);
    s_proxy_server->start();

    while (PthTask::activeCount() > 0) {
        PthTask::sleep(1);
    }
}
