#ifndef __PTH_SOCKET_H__
#define __PTH_SOCKET_H__

#include <string>
using namespace std;

class PthSocket
{
  public:
    bool error;
    char errstr[128];
    string errmsg_;
    int sockfd;
    char ip_addr[64];

  private:
    char *LookAhead_bytes;
    int LookAhead_len;
    int LookAhead_capacity;

  private:
    void lookahead_del_front(int n);
    void lookahead_add(char *str, int n);
    int lookahead_eol_count();
    int lookahead_len();
    char *lookahead_ptr0();
    int lookahead_find_eol();
    void lookahead_init();
    void lookahead_destroy();

  private:
    void create(const char *ip, int port, int timeout = 0);
    void init();

  public:
    PthSocket();

  public:
    PthSocket(int port);
    PthSocket(char *ip, int port, int timeout = 0);
    PthSocket(const string &ip, int port, int timeout = 0);

    virtual ~PthSocket();

  public:
    PthSocket *accept(int timeout = 0);

    char *peer_addr();
    string peeraddr();

    char *peer_name(char *ip_addr_buf = NULL);
    string peername();

    int peerport();
    int myport();

    int readline(char *buf /* [BUF_SIZ=4096] */, int timeout = 0);
    int read(char *buf /* [size] */, int size, int timeout = 0);

    // 2004/04/20 write() default timeout을 0초에서 60초로 바꿈.
    // 2004/10/7 smy write default timeout을 60초에서 5초로 바꿈.
    int write(const char *buf /* [len] */, int len, int timeout = 5);

  public:
    string read_line(int timeout = 0);
    int read_line(string &line, int timeout = 0);

    // 2004/10/7 smy 두개의 write_line함수를 사용할때 argument를 2개 주면 어떤
    // 함수를 사용해야할 지 컴파일러가 모르게 되는 문제로 인하여 변경하였음.
    // 2004/10/7 smy write default timeout을 60초에서 5초로 바꿈.
    //size_t write_line(const void *buf, size_t size, int timeout = 60);
    size_t write_line(const void *buf, size_t size, int timeout);
    void write_line(const string &line, int timeout = 5);

    void close();

    bool is_Error();
    int isError();

    string getErrMsg(); 
    char *getErrStr(); 
    int getSockFd(); 

    void set_sockfd(int sockfd); 
    char *getIpAddr(); 

  public:
    static void set_rlimit_max();
};

#endif // __PTH_SOCKET_H__

