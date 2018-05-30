#ifndef _SecureProxy_h_
#define _SecureProxy_h_

#include <string>
using namespace std;

#include "PthTask.h"
#include "PthSocket.h"

// private
class ProxyChannel: public PthTask
{
  private:
    PthSocket *s_sock;
    PthSocket *t_sock;
    string key;

  private:
    string encrypt(const string &data);
    string decrypt(const string &data);

  public:
    ProxyChannel(PthSocket *s_sock, PthSocket *t_sock, const string &key);
    ~ProxyChannel();

  public:
    void run();
};

// public
class SecureProxyServer: public PthTask
{
  private:
    int s_port;
    string t_ip;
    int t_port;
    string shared_key;

  private:
    string CRAM_MD5_server(PthSocket *s_sock);

  public:
    SecureProxyServer(int s_port, const string &t_ip, int t_port,
                      const string &shared_key);
    ~SecureProxyServer();

    void run();
};

// public
class SecureProxyClient: public PthTask
{
  private:
    int t_port;
    string s_ip;
    int s_port;
    string shared_key;

  private:
    string CRAM_MD5_client(PthSocket *s_sock);

  public:
    SecureProxyClient(int t_port, const string &s_ip, int s_port,
                      const string &shared_key);

    ~SecureProxyClient();

  public:
    void run();
};

#endif // _SecureProxy_h_
