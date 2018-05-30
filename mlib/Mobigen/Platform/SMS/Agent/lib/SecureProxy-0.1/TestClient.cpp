#include <string>
#include <stdio.h>
using namespace std;

#include "StrUtil.h"
#include "PthTask.h"
#include "SecureProxy.h"

int main(int argc, char *argv[])
{
    if (argc < 4) {
        printf("Usage: %s text_listen_port secure_ip:secure_port shared_key\n",
            argv[0]);
        exit(0);
    }

    int t_port = atoi(argv[1]);
    vector<string> ip_port = StrUtil::split(argv[2], ":", 2);
    string s_ip = ip_port[0];
    int s_port = StrUtil::string2int(ip_port[1]);
    string shared_key = argv[3];
    

    SecureProxyClient *s_proxy_client =
         new SecureProxyClient(t_port, s_ip, s_port, shared_key);
    s_proxy_client->set_auto_delete(true);
    s_proxy_client->start();

    //while (PthTask::activeCount() > 0) {
    while (true) {
        PthTask::sleep(1);
    }
}
