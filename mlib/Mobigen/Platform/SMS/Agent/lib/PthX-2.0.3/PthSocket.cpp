// ---------------------------------------------------------------------------
// PthSocket.cpp --
//   GNU Pth 라이브러리의 pth_socket 을 확장하여, C++인터페이스를 만들었음.
//
// Author: All rights reserved. (c) Mobigen Co., Ltd.
//
// Updates:
//   2003/12/27 wait_socket_ready()에 EAGAIN 이 나올 경우, true를 리턴하도록
//              수정함.
// ---------------------------------------------------------------------------

#include <unistd.h> // close()

#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <stdlib.h>

#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>

#include <fcntl.h> // fcntl()

#include <ctype.h> // isdigit()

#include <time.h>
#include <sys/types.h> // for ClsTCP Interface
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#include <sys/poll.h>

#include <errno.h>
#include <netdb.h>   // gethostbyname()
#include <time.h> // time()

#include <map>

using namespace std;

#include "PthTask.h"
#include "PthSocket.h"

#ifndef DEBUG_PRINT
#  ifdef NDEBUG
#    define DEBUG_PRINT if (0) printf
#  else // NDEBUG
#    define DEBUG_PRINT printf("(%s,%d) ", __FILE__, __LINE__); printf
#  endif // NDEBUG
#endif // DEBUG_PRINT

typedef struct sockaddr_in SockAddrIn;
typedef struct sockaddr SockAddr;

typedef struct in_addr InAddr;
typedef struct hostent HostEnt;

#include <stdio.h>
#include <sys/resource.h>
#include <unistd.h>

#ifdef __linux__
    #define SockLen socklen_t
#else
  #ifdef _SOCKLEN_T
    #define SockLen socklen_t
  #else
    #define SockLen int
    /* 솔라리스2.6에서는 왜 socklen_t가 없는 거야!!! */
  #endif
#endif

static void __usleep(int micro_sec)
{
    struct timeval tval;
    tval.tv_sec = micro_sec / 1000000;
    tval.tv_usec = micro_sec % 1000000;

    ::select(0, (fd_set *)NULL, (fd_set *)NULL, (fd_set *)NULL, &tval);
}

bool PthSocket::is_Error()
{
    if (this->error) {
        this->errmsg_ = this->errstr;
    }
    return this->error;
}

int PthSocket::isError()
{
    if (this->error) {
        this->errmsg_ = this->errstr;
    }
    return (int) this->error;
}

string PthSocket::getErrMsg()
{
    return string(this->errstr);
}

char *PthSocket::getErrStr()
{
    return this->errstr;
}

int PthSocket::getSockFd()
{
    return this->sockfd;
}

void PthSocket::set_sockfd(int sockfd)
{
    this->sockfd = sockfd;
}

char *PthSocket::getIpAddr()
{
    return this->ip_addr;
}

void PthSocket::set_rlimit_max()
{
    struct rlimit rlim;

    rlim.rlim_cur = 256;
    rlim.rlim_max = 256;
    if (setrlimit(RLIMIT_NOFILE, &rlim) != 0) {
        fprintf(stderr, "(%s,%d) setrlimit fail(%s)\n", __FILE__, __LINE__,
            strerror(errno));
    }

    struct rlimit cur_rlim;
    if (getrlimit(RLIMIT_NOFILE, &cur_rlim) != 0 )
    {
       fprintf(stderr, "(%s,%d) getrlimit fail(%s)\n", __FILE__, __LINE__,
           strerror(errno));
    }

    fprintf(stderr, "(%s,%d) after open file(%d:%d)\n",
           __FILE__, __LINE__, 
           (int)cur_rlim.rlim_cur, (int)cur_rlim.rlim_max);
}

void PthSocket::init()
{
    this->error = false;
    this->errstr[0] = '\0';
    this->sockfd = -1;
    this->ip_addr[0] = '\0';

    this->lookahead_init();
}

PthSocket::~PthSocket()
{
    this->lookahead_destroy();
}

PthSocket::PthSocket()
{
    this->init();
}

int _set_NonBlock(int sock_fd)
{
    int ret = fcntl(sock_fd, F_SETFL, O_NDELAY);
    return ret;
}

PthSocket::PthSocket(int port)
{
    assert(port > 0);

    this->init();

    if ((this->sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        DEBUG_PRINT("PthSocket: socket() fail: %d:%s\n", errno, 
            strerror(errno));
        this->error = true;
        strcpy(this->errstr, "ServerSock: socket() fail");
        return;
    }

    _set_NonBlock(this->sockfd);

    SockAddrIn serv_addr;
    memset((char *)&serv_addr, '\0', sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    serv_addr.sin_port = htons(port);

    // Set an option on the socket to enable local address reuse
    int opt = 1;
    if (setsockopt(this->sockfd,
       SOL_SOCKET, SO_REUSEADDR, (char *)&opt, sizeof(opt)) < 0)
    {
        DEBUG_PRINT("setsockopt(SO_REUSEADDR) error.\n");
        this->error = true;
        strcpy(this->errstr, "setsockopt(SO_REUSEADDR) error");
        return;
    }

  if (0) // 꼭 필요한가?
  {
    // setsockopt(SO_KEEPALIVE) introduced
    opt = 0;
    if (setsockopt(this->sockfd, SOL_SOCKET, SO_KEEPALIVE,
           (char *)&opt, sizeof(opt)) < 0)
    {
        DEBUG_PRINT("setsockopt(SO_KEEPALIVE) error.\n");
        this->error = true;
        strcpy(this->errstr, "setsockopt(SO_KEEPALIVE)");
        return;
    }
  }

    if (bind(this->sockfd, (SockAddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        DEBUG_PRINT("PthSocket: bind() fail\n");
        this->error = true;
        strcpy(this->errstr, "PthSocket: bind() fail");
        return;
    }

    strcpy(this->ip_addr, inet_ntoa(serv_addr.sin_addr));

    if (listen(this->sockfd, 64) < 0) {
        DEBUG_PRINT("PthSocket: listen() fail\n");
        this->error = true;
        strcpy(this->errstr, "PthSocket: listen() fail");
        return;
    }
}

static bool __isNumeric(const char *hostAddr)
{
    assert(hostAddr != NULL);

    char *host = (char*) hostAddr;
    if (host == NULL) return (false);
    while (*host != '\0') {
        if (! isdigit((int)(*host)) && *host != '.')
            return (false);
        host++;
    }
    return (true);
}

#define __READ_FLAG 0
#define __WRITE_FLAG 1

static
bool wait_socket_ready_POLL(int sockfd, int timeout, int read_write_flag)
{
    assert(sockfd > 0);
    assert(timeout >= 0);
    assert(read_write_flag == __READ_FLAG || read_write_flag == __WRITE_FLAG);

    if (timeout == 0) {
    return false; // TIMEOUT!
    }

    struct pollfd wait_fd;
    wait_fd.fd = sockfd;

    if (read_write_flag == __READ_FLAG) { // read wait
        wait_fd.events = POLLIN;
    } else if (read_write_flag == __WRITE_FLAG) { // write wait
        wait_fd.events = POLLOUT;
    }

    errno = 0;
    int r = ::poll(&wait_fd, 1, timeout*1000);

    if (r == 0) {
        return false;  // TIMEOUT, A value of 0 indicates
                       // that the call timed out and
                       // no file descriptors have  been selected.
    }

    if (r < 0) {
        return false;  // ERROR, On  error,  -1  is  returned, 
                       // and errno is set appropriately
    }

    // 2004.05.27 
    if (wait_fd.revents & (POLLERR | POLLHUP)) {
        return false;
    }

    if ((read_write_flag == __READ_FLAG && (wait_fd.revents & POLLIN)) ||
    (read_write_flag == __WRITE_FLAG && (wait_fd.revents & POLLOUT)))
    {
        if (wait_fd.revents & POLLERR) {
            return false;
        }

    return true; 
    }

    assert(0); // 여기오면 안 되는데...

    return false;
}

static
bool wait_socket_ready_SELECT(int sockfd, int timeout, int read_write_flag)
{
    assert(sockfd > 0);
    assert(timeout >= 0);
    assert(read_write_flag == __READ_FLAG || read_write_flag == __WRITE_FLAG);

    // connect 진행중, write_select를 해서 connect가 끝날 때까지 기다림.
    fd_set wfds; FD_ZERO(&wfds);
    fd_set rfds; FD_ZERO(&rfds);
    fd_set efds; FD_ZERO(&efds);

    if (timeout == 0) {
// DEBUG_PRINT("timeout\n");
        return false; // TIMEOUT!
    }

    if (read_write_flag == __READ_FLAG) { // read wait
        FD_SET(sockfd, &rfds);
    } else if (read_write_flag == __WRITE_FLAG) { // write wait
        FD_SET(sockfd, &wfds);
    }
    FD_SET(sockfd, &efds);

    struct timeval tv;
    tv.tv_sec = timeout;
    tv.tv_usec = 0;

//    int EAGAIN_count = 0;
// try_select_again:

    errno = 0;
    int r = ::select(sockfd+1, &rfds, &wfds, &efds, &tv); // WAIT
    // int r = ::select(sockfd+1, &rfds, &wfds, &efds, &tv); // WAIT

    if ((read_write_flag == __READ_FLAG && FD_ISSET(sockfd, &rfds)) ||
        (read_write_flag == __WRITE_FLAG && FD_ISSET(sockfd, &wfds)))
    {
        // --------------------------------------------------------------
        // 2003/12/27 EAGAIN 인 상황은 정상인 상황이므로, read/write 를
        //            시도할 수 있도록 true를 리턴한다.
        // --------------------------------------------------------------
        if (FD_ISSET(sockfd, &efds) == 0 && errno == EAGAIN /* 11 */) {
            // 에러가 아니면서, Resource temporarily unavailable 이 나오면
            // DEBUG_PRINT("try_select_again: errno=%d\n", errno);

         // if (EAGAIN_count++ > 10) {
         //     return false;
         // }

         // pth_yield(NULL);
         // goto try_select_again;
  
            return true;
        }

        // 2003/12/02 exception handling added
        if (FD_ISSET(sockfd, &efds) || errno != 0) {
            DEBUG_PRINT("efds is set:%d, errno:%d, r:%d\n",
               (int) FD_ISSET(sockfd, &efds), errno, r);
            return false;
        }

    // assert(r == 1);

        if (errno != 0) {
            DEBUG_PRINT("errno[%d] != 0, r:%d\n", errno, r);
        }

        return true; 
    }

    if (r == 0 && errno == 0) {
        // DEBUG_PRINT("r == 0 && errno == 0, return false\n");
        return false;
    }

    // printf("r:%d, errno:%d, errstr:%s\n", r, errno, strerror(errno));
    if (! ((r == 0  && errno == 11) || (r == -1 && errno != 0))) {
        DEBUG_PRINT("r=%d, errno=%d, error=%s\n", r, errno, strerror(errno));
    }
    assert((r == 0  && errno == 11) || (r == -1 && errno != 0));

    // DEBUG_PRINT("return false; // TIMEOUT\n");

    return false; // TIMEOUT
}


static
bool wait_socket_ready(int sockfd, int timeout, int read_write_flag)
{
  if (0) {
    return wait_socket_ready_SELECT(sockfd, timeout, read_write_flag);
  }

  if (1) {
    return wait_socket_ready_POLL(sockfd, timeout, read_write_flag);
  }
}


void PthSocket::create(const char *remoteHost, int port,
                       int timeout) // default = 0
{
    assert(remoteHost != NULL);
    assert(port >= 0);

    // DEBUG_PRINT("Client ClsTCP(%s,%d)\n", remoteHost, port);

    this->init();

    InAddr addr;
  if (! __isNumeric(remoteHost)) {
    HostEnt *hostptr = gethostbyname(remoteHost);
    if (hostptr == NULL) {
        DEBUG_PRINT("ClientClsTCP: gethostbyname(%s) fail\n", remoteHost);
        this->error = true;
        strcpy(this->errstr, "ClientClsTCP: gethostbyname() fail");
        return;
    }
    (void) memcpy(&addr.s_addr, hostptr->h_addr, sizeof (addr.s_addr));
  } else {
    addr.s_addr = inet_addr(remoteHost);
  }

    SockAddrIn serv_addr;
    memset((char *)&serv_addr, '\0', sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    memcpy(&serv_addr.sin_addr.s_addr, &addr.s_addr, 4);
    serv_addr.sin_port = htons(port);

    if ((this->sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
    DEBUG_PRINT("ClientClsTCP: socket() fail: %d:%s\n",
             errno, strerror(errno));
    this->error = true;
    strcpy(this->errstr, "PthSocket: socket() fail");
    return;
    }

    _set_NonBlock(this->sockfd);

  if (0) { // Client Socket에서는 SO_REUSEADDR할 필요 없음. (??)
    int opt = 1;
    if (setsockopt(this->sockfd,
       SOL_SOCKET, SO_REUSEADDR, (char *)&opt, sizeof(opt)) < 0)
    {
    DEBUG_PRINT("setsockopt(SO_REUSEADDR) error.\n");
    this->error = true;
    strcpy(this->errstr, "setsockopt(SO_REUSEADDR) error");
    return;
    }
  }

  if (0) { // 꼭 필요한가?
    // setsockopt(SO_KEEPALIVE) introduced
    int opt = 0;
    if (setsockopt(this->sockfd, SOL_SOCKET, SO_KEEPALIVE,
       (char *)&opt, sizeof(opt)) < 0)
    {
    DEBUG_PRINT("setsockopt(SO_KEEPALIVE) error.\n");
    this->error = true;
    strcpy(this->errstr, "setsockopt(SO_KEEPALIVE)");
    return;
    }
  }

    errno = 0;

    // int r = pth_connect(this->sockfd,
    //     (SockAddr *)&serv_addr,sizeof(serv_addr));
    int r = ::connect(this->sockfd, (SockAddr *)&serv_addr,sizeof(serv_addr));

    if (r == 0) {
// DEBUG_PRINT("ready\n");
        // 곧바로 connect 성공
        this->error = false;
        strcpy(this->ip_addr, inet_ntoa(serv_addr.sin_addr));
        return;
    } else if (r < 0 && errno == EINPROGRESS) {
        bool ready = false;

        if (timeout == 0) {
            ready = wait_socket_ready(this->sockfd, 1000000, __WRITE_FLAG);
        } else {
            ready = wait_socket_ready(this->sockfd, timeout, __WRITE_FLAG);
        }

        if (ready) {
            // 기다렸다가 connect 성공
// DEBUG_PRINT("errno:%d, r:%d\n", errno, r);
            this->error = false;
            strcpy(this->ip_addr, inet_ntoa(serv_addr.sin_addr));
            return;
        } else {
            // pth_yield(NULL);
            // 실패한 경우
            this->error = true;
            ::close(this->sockfd);
            this->sockfd = -1;
            strcpy(this->errstr, "pth_connect() timeout");
            return;
        }
    } else {
        // 오류가 난 상태임.
        ::close(this->sockfd);
        this->error = true;
        strcpy(this->errstr, "pth_connect() failed\n");
    }
}

PthSocket::PthSocket(const string &remoteHost, int port,
                    int timeout) // default = 0
{
    this->create(remoteHost.c_str(), port, timeout);
}

PthSocket::PthSocket(char *remoteHost, int port,
                    int timeout) // default = 0
{
    this->create(remoteHost, port, timeout);
}

int _set_Linger(int sock_fd, int sec)
{
    int optval[2];
        optval[0] = 1;        // LINGER_ON
        optval[1] = sec;        // SEC

    int ret = setsockopt(sock_fd, SOL_SOCKET,
        SO_LINGER, (const char *)optval, (size_t)2 * sizeof(int));

    return ret;
}

#ifdef TIME_DEBUG
std::map<int,int> time_count;

time_t TIME(int line)
{
    if (time_count.find(line) == time_count.end()) {
        time_count[line] = 0;
    } else {
        time_count[line] += 1;

        if (time_count[line] % 5) {
            DEBUG_PRINT("line:%d, count:%d\n", line, time_count[line]);
        }
    }

    return time(NULL);
}
#else
  #define TIME(x) time(NULL)
#endif // TIME_DEBUG

PthSocket *PthSocket::accept(int timeout) // default = 0
{
    // DEBUG_PRINT("Listening...\n");

    SockAddrIn cli_addr;

    SockLen cli_len = sizeof(cli_addr);

    time_t t_start = TIME(__LINE__);
    int new_sockfd = -1;

    int t_rest = timeout; // timeout을 적용하여 기다릴 수 있는 초길이
    while (1) {
        bool ready = false;
        if (timeout > 0) { // timeout == 0 이면, 무한히 기다리도록 함.
            ready = wait_socket_ready(this->sockfd, t_rest, __READ_FLAG);
        } else {
            ready = wait_socket_ready(this->sockfd, 1000000, __READ_FLAG);
        }

        if (! ready) { // TIMEOUT
            // pth_yield(NULL);
            return NULL;
        }

        errno = 0;

        //static PthLock accept_lock;
        
        //accept_lock.lock();

        //new_sockfd = pth_accept(this->sockfd,(SockAddr*)&cli_addr,&cli_len);
        new_sockfd = ::accept(this->sockfd, (SockAddr *)&cli_addr, (socklen_t*)&cli_len);

        //accept_lock.unlock();

        if (new_sockfd < 0 && errno == EAGAIN) {
            t_rest = timeout - (TIME(__LINE__) - t_start);
            if (timeout > 0 && t_rest <= 0) {
                DEBUG_PRINT("PthSocket: accept() fail: %s\n", strerror(errno));
                // pth_yield(NULL);
                return NULL;
            }
            else {
                // Pth:yield();
                // pth_yield(NULL);
                continue;
            }
        } else if (new_sockfd < 0) {
            DEBUG_PRINT("PthSocket: accept() fail: %s\n", strerror(errno));
            // pth_yield(NULL);
            return NULL;
        } else if (new_sockfd > 0) {
            break; 
        }
    }

    _set_NonBlock(this->sockfd);
    _set_Linger(new_sockfd, 0);

    PthSocket *pNewSock = new PthSocket();
    if (pNewSock == NULL || pNewSock->error) {
        DEBUG_PRINT("ServerPthSocket: new child PthSocket() fail\n");
        return NULL;
    }

    pNewSock->sockfd = new_sockfd;
    strcpy(pNewSock->ip_addr, inet_ntoa(cli_addr.sin_addr));

    return pNewSock;
}

// -----------------------------

void PthSocket::lookahead_init()
{
    this->LookAhead_len = 0;
    this->LookAhead_capacity = 512;

    // capacity크기 만큼 메모리를 잡아둔다.
    this->LookAhead_bytes =
        (char *) malloc(this->LookAhead_capacity * sizeof(char) + 1);

    assert(this->LookAhead_len == 0);
    assert(this->LookAhead_capacity > 0);
}

void PthSocket::lookahead_destroy()
{
     free(this->LookAhead_bytes);
}

int PthSocket::lookahead_find_eol()
{
    // 특정 소켓의 룩어헤드 버퍼에서 '\n'을 찾아내기.
    // 룩어헤드 버퍼내의 첫번째 '\n'의 상대적인 위치를 리턴한다
    // '\n'이 없으면 -1을 리턴

    // 가정: LookAhead_bytes에는 '\0'이 아닌 글자만 들어간다.

    assert(this->LookAhead_capacity > 0);
    assert(this->LookAhead_bytes != NULL);
    assert(this->LookAhead_len >= 0);
    assert(this->LookAhead_capacity >= this->LookAhead_len);

    // 스트링 검색에서 '\0'까지만 해야 함. 스트링의 끝을 마킹함.

// DEBUG_PRINT("this->LookAhead_len:%d, this->LookAhead_capacity:%d\n",
//      this->LookAhead_len, this->LookAhead_capacity);

    this->LookAhead_bytes[this->LookAhead_len] = '\0';

    char *p = strchr(this->LookAhead_bytes, '\n');

    if (p == NULL) { /* '\n' 발견되지 않았음 */
        return -1;
    }

    assert((p - this->LookAhead_bytes) >= 0);
    assert((p - this->LookAhead_bytes) <= this->LookAhead_len);

    // '\n'의 상대적인 위치를 리턴한다 
    return (p - this->LookAhead_bytes);
}

char *PthSocket::lookahead_ptr0()
{
    return this->LookAhead_bytes;
}

int PthSocket::lookahead_len()
{
    return this->LookAhead_len;
}

void PthSocket::lookahead_del_front(int n)
{
    // 특정 소켓에 할당된  룩어헤드 버퍼에서, 처음 n바이트를 지운다. 
    assert(n > 0);
    assert(n <= this->LookAhead_len);
    assert(this->LookAhead_capacity > 0);

    memmove(this->LookAhead_bytes,
            this->LookAhead_bytes + n,
            this->LookAhead_len - n);

    this->LookAhead_len -= n; // 버퍼의 길이가 줄어듬 

    assert(this->LookAhead_capacity > 0);
}

void PthSocket::lookahead_add(char *ptr, int n)
{

    // 특정 소켓의 룩어헤드 버퍼에 ptr이 가리키고 있는 n바이트를 추가하기 
    assert(ptr != NULL);
    assert(n > 0);

    assert(this->LookAhead_capacity > 0);

    // '\0'제거 
    if (1) {
        int null_count = 0;
        // 입력된 ptr[0..n]속에 '\0'가  들어 있음. 그것들을 공백으로 바꿈.
        for (int i = 0; i < n; i++) {
            if (ptr[i] == '\0') {
                ptr[i] = ' ';
                null_count++;
            }
        }
        if (null_count > 0) {
            ptr[n] = '\0';
        }
    }

    if (this->LookAhead_len + n <= this->LookAhead_capacity) {
        // 만약 기존의 버퍼 공간이 충분하면, 뒤에 바로 추가한다. 
        assert(this->LookAhead_capacity > 0);

        memcpy(this->LookAhead_bytes + this->LookAhead_len, ptr, n);

        assert(this->LookAhead_capacity > 0);

        this->LookAhead_len += n;

        assert(this->LookAhead_capacity > 0);
    } else {
        // 공간이 부족하면 realloc()으로 공간을 할당받고 추가한다. 

        assert(this->LookAhead_capacity > 0);

        this->LookAhead_bytes = (char*)
             realloc(this->LookAhead_bytes, this->LookAhead_len + n + 1);

        assert(this->LookAhead_capacity > 0);

        this->LookAhead_capacity = this->LookAhead_len + n;

        assert(this->LookAhead_capacity > 0);

        memcpy(this->LookAhead_bytes + this->LookAhead_len, ptr, n);

        this->LookAhead_len += n;

        assert(this->LookAhead_capacity > 0);
     }

     assert(this->LookAhead_len >= n);
     assert(this->LookAhead_capacity >= this->LookAhead_len);
}

int PthSocket::lookahead_eol_count()
{
    // 특정 소켓의 룩어헤드 버퍼에서 '\n'의 갯수를 세기
    // 가정: LookAhead[].bytes에는 '\0'이 아닌 글자만 들어간다.

    int count = 0;
    for (int i = 0; i < this->LookAhead_len; i++) {
        if (this->LookAhead_bytes[i] == '\n') {
            count++;
        }
    }

    return count;
}

int PthSocket::read(char *buf, int size,
                   int timeout) // default = 0
{
    // 주의: buf에는 반드시 size만큼 메모리가 할당되어 있어야 함.

    assert(this->sockfd >= 0);
    assert(buf != NULL);

    time_t t_start = TIME(__LINE__);

    int curSize = 0;
    while (1) {
        bool ready = false;

        // DEBUG_PRINT("is_ready()\n");

        if (timeout == 0) {
            ready = wait_socket_ready(this->sockfd, 1000000, __READ_FLAG);
        } else {
            int t_rest = timeout - (TIME(__LINE__) - t_start);
            if (t_rest <= 0) {
                // eek add 
                this->error = true;
                return -1;
            }
            ready = wait_socket_ready(this->sockfd, t_rest, __READ_FLAG);
        }

        if (! ready) {
            this->error = true;
            return -1;
        }

        errno = 0;

        assert(curSize >= 0 && curSize < size);

        // int n = // pth_read(this->sockfd, &buf[curSize], size - curSize);
        int n = ::read(this->sockfd, &buf[curSize], size - curSize);

        if (n <= 0 && errno == EAGAIN) {
            assert(curSize == 0);
            // Pth::yield();
            // pth_yield(NULL);
            continue;
        }

        if (n == 0 || /* read()의 결과가 n == 0이면 EOF를 의미한다. */
            errno == EBADF || /* Bad File Descriptor */
            errno == ECONNRESET || /* Connection reset by peer */
            errno == ENOTCONN ||   /* Transport endpoint is not connected */
            errno == ECONNABORTED || /* Software caused connection abort */
            errno == EINVAL || /* Invalid */
            errno == EIO || /* IO FAIL */
            errno == EPIPE || /* PIPE FAIL */
            0
           )
        {
           this->error = true;
            n = 0;
            return n;
        }

        if (n < 0) {
            // n이 0보다 작으면 어떤 식으로든 errno가 적혀 있다.
            // errno == EAGAIN이면 새로 읽고 그렇지 않으면 소켓을 close하면 됨.
            this->error = true;
            return -1;
        }

        // 새로 n 바이트만큼을 읽어 낸 상태임.
        assert(n > 0);

        curSize = curSize + n;

        assert(curSize >= 0 && curSize <= size);

        this->error = false;
        return curSize;
    }
}

string PthSocket::read_line(int timeout) // default = 0
{
    string result = "";

    char buf[BUFSIZ];

    int r = this->readline(buf, timeout);

    if (r >= 0) {
        result = buf;
    }

    return result;
}

int PthSocket::read_line(string &result, int timeout)
{
    char buf[BUFSIZ];
    int r = this->readline(buf, timeout);

    if (r >= 0) {
        buf[r] = '\0';
        result = buf;
    }

    return r;    
}

void PthSocket::write_line(const string &line,
                       int timeout) // default = 0
{
    assert(timeout == timeout); // unused timeout

    this->write((char*) line.c_str(), line.size(), timeout);
}

size_t PthSocket::write_line(const void *buf, size_t size, int timeout)
{
    assert(timeout == timeout); // unused timeout

    return this->write((char*) buf, size, timeout);
}

int PthSocket::readline(char *buf, int timeout /*= 0*/) 
{
    /* sizeof(buf) == BUFSIZ */

    // 주의: buf에는 반드시 BUFSIZ만큼 메모리가 할당되어 있어야 함.

    // 특정 소켓으로 부터 자료를 읽어서 그중 한 라인을
    // buf에 strcpy()해 주고, 그 길이를 리턴한다.

    static char buf_tmp[BUFSIZ+1]; // static 해야 함. 스택에 쌓이지 않게 

    assert(this->sockfd >= 0);
    assert(buf != NULL);

    int eol_pos = this->lookahead_find_eol();
    if (eol_pos >= 0) {
        memcpy(buf, this->lookahead_ptr0(), eol_pos+1);
        buf[eol_pos+1] = '\0';

        assert(this->lookahead_len() >= eol_pos+1);
        this->lookahead_del_front(eol_pos+1);

        // DEBUG_PRINT("read from lookahead: [%s]\n", buf);
 
        this->error = false;
        return eol_pos+1;
    }

    assert(this->lookahead_eol_count() == 0);

  {
    // '\n'없이 버퍼 전체가 꽉 찼을 경우, 실제 read하지 않고,
    //  버퍼의 절반을 '\n'없이 리턴한다.

    if (this->lookahead_len() >= BUFSIZ) {
        // 강제로 라인을 잘라서 리턴해야 함
        // 잘린 라인에는 '\n'이 들어 있지 않음
        eol_pos = BUFSIZ/2 - 1; /* 2048 - 1 == 2047 */

        memcpy(buf, this->lookahead_ptr0(), eol_pos+1);
        buf[eol_pos+1] = '\0';

        assert(this->lookahead_len() >= eol_pos+1);
        this->lookahead_del_front(eol_pos+1);

        this->error = false;
        return eol_pos+1;
    }
  }

    // 룩어헤드 버퍼에 한줄이 채 없으면, 새로 읽어서 한 줄 이상을
    // 버퍼에 채워 넣으려고 시도한다.
    // BUFSIZ이상을 LookAhead 버퍼에 쌓아 두지 않는다.
    // 읽어들인 버퍼에 '\0'이 있을 수 있음. --> 공백으로 바꿈.

    assert(timeout == timeout);
    time_t t_start = TIME(__LINE__);

    while (1) {
        bool ready = false;
        //  ready = wait_socket_ready(this->sockfd, 1000000, __READ_FLAG);

/// ????? 이부분을 왜 주석 처리 했는가??????????
        if (timeout == 0) {
            // 무한히 기다리는 모드, 굳이 wait_ready를 할 필요 없음.
            ready = wait_socket_ready(this->sockfd, 1000000, __READ_FLAG);
        } else {
            int t_rest = timeout - (TIME(__LINE__) - t_start);
            if (t_rest <= 0) {
                // eek add 
                this->error = true;
                return -1;
            }
            ready = wait_socket_ready(this->sockfd, t_rest, __READ_FLAG);
        }
/// ????? 이부분을 왜 주석 처리 했는가??????????

      {
        // 2003/03/17 버퍼 크기 체크 
        //   '\n'없이 버퍼 전체가 꽉 찼을 경우, 실제 read하지 않고,
        //   버퍼의 일부를 '\n'없이 리턴한다.

        if (this->lookahead_len() >= BUFSIZ-1) {
            // 강제로 라인을 잘라서 리턴해야 함
            // 잘린 라인에는 '\n'이 들어 있지 않음
            eol_pos = BUFSIZ-2; /* 1024 - 2 == 1022 */

            memcpy(buf, this->lookahead_ptr0(), eol_pos+1); // 0 ~ 1022
            buf[eol_pos+1] = '\0'; //1023

            assert(this->lookahead_len() >= eol_pos+1);
            this->lookahead_del_front(eol_pos+1);

            this->error = false;
            return eol_pos+1;
        }
      }

        assert(BUFSIZ-this->lookahead_len() > 0);

        if (! ready) {
            this->error = true;
            return -1;
        }

        errno = 0;
        // int n = pth_read(this->sockfd,buf_tmp,BUFSIZ-this->lookahead_len());
        int n = ::read(this->sockfd, buf_tmp, BUFSIZ-this->lookahead_len());

        if (n <= 0 && errno == EAGAIN && this->lookahead_len() > 0) {
            int t_diff1 = (int)(TIME(__LINE__) - t_start);

            // timeout초 이내에 '\n'없는 데이타가 버퍼에
            // 계속 쌓여 있을 경우에는, 할 수 없이 flush를 시켜 준다. 
            if (timeout > 0 && t_diff1 > timeout) {
                this->error = true; // eek
                return -1; // 못 읽었음.
            } else if (timeout == 0) {
                // Pth::yield();
                // pth_yield(NULL);
                continue;
            } else {
                // 이때는 어떻게?
            }
        }


        if (n == 0 || /* read()의 결과가 n == 0이면 EOF를 의미한다. */
            errno == EBADF || /* Bad File Descriptor */
            errno == ECONNRESET || /* Connection reset by peer */
            errno == ENOTCONN ||   /* Transport endpoint is not connected */
            errno == ECONNABORTED || /* Software caused connection abort */
            errno == EINVAL || /* Invalid */
            errno == EIO || /* IO FAIL */
            errno == EPIPE || /* PIPE FAIL */
            0
           )
        {
            // 2004/08/03 소켓이 닫혔는데, buffer에 뭔가 있으면...
            if (this->lookahead_len() > 0) {
                // lookahead 전체를 리턴함.

                int lookahead_len = this->lookahead_len();
                memcpy(buf, this->lookahead_ptr0(), lookahead_len);
                buf[lookahead_len] = '\0';

                this->lookahead_del_front(lookahead_len);

                this->error = false;
                return lookahead_len;
            }

            this->error = true;
            n = 0;
            return n;
        }

        if (n < 0) {
            // n이 0보다 작으면 어떤 식으로든 errno가 적혀 있다.
            // errno == EAGAIN이면 새로 읽고 그렇지 않으면 소켓을 close하면 됨.
            this->error = true;
            return -1;
        }

        // 새로 n 바이트만큼을 읽어 낸 상태임.
        assert(n > 0);

        // 읽어낸 n바이트를 우선 룩어헤드 버퍼에 넣고, 그 후에 첫 한 줄을 
        // 찾아서 buf에 복사하고 그 길이를 리턴한다. 

        assert(buf != NULL); // 리턴시켜줘야할 버퍼 
        assert(this->lookahead_ptr0() != NULL);
        assert(this->lookahead_len() >= 0);
        assert(buf_tmp != NULL);

        assert(this->LookAhead_capacity > 0);
        this->lookahead_add(buf_tmp, n);

        // 새로 읽은 버퍼에서 newline을 찾으면 한 라인만 잘라서 리턴 
        int eol_pos = this->lookahead_find_eol();
        if (eol_pos >= 0) {
            memcpy(buf, this->lookahead_ptr0(), eol_pos+1);
            buf[eol_pos+1] = '\0';

            assert(this->lookahead_len() >= eol_pos+1);
            this->lookahead_del_front(eol_pos+1);

            this->error = false;
            return eol_pos+1;
        }
    }
}

int PthSocket::write(const char *buf, int len, int timeout)
{
    assert(buf != NULL);
    assert(len >= 0);

    int len_tmp = len;
    int n = 0;

    // time_t t1 = time(NULL);
    // time_t t2 = time(NULL);
    // time_t t3 = time(NULL);
    // time_t t4 = time(NULL);
    errno = 0;
    // int n = pth_write(this->sockfd, buf, len);

    char *pBuf = (char *)&buf[0];

    time_t t0 = time(NULL);

  write_again:
    assert(pBuf < (&buf[0] + len));
    int n_tmp = ::write(this->sockfd, pBuf, len_tmp); // Non-Block Socket임.

    if (n_tmp > 0) {
        assert(len_tmp >= n_tmp);
        n += n_tmp;
    }

    // time_t t5 = time(NULL);
    // time_t t6 = time(NULL);
    // time_t t7 = time(NULL);
    // time_t t8 = time(NULL);

    if (n_tmp != len_tmp) {
        if (
            errno == EBADF || /* Bad File Descriptor */
            errno == ECONNRESET || /* Connection reset by peer */
            errno == ENOTCONN ||   /* Transport endpoint is not connected */
            errno == ECONNABORTED || /* Software caused connection abort */
            errno == EINVAL || /* Invalid */
            errno == EIO || /* IO FAIL */
            errno == EPIPE || /* PIPE FAIL */
            0
           )
        {
            /* ERROR */
            this->error = true;
            // goto write_end; // 필요 없음.
        } else if (n_tmp == -1 && errno == EAGAIN) {
            /* EAGAIN */
            // assert(len_tmp > n_tmp);
            // len_tmp -= n_tmp;
            // Pth::yield();
            int t_diff = (int) (time(NULL) - t0);

            // 2003-05-27 Write 실패시 timeout만큼 재시도 함.
            if (timeout == 0) {
                // Timeout이 0이면, 무한히 반복되는 한이 있더라도 재시도
                // pth_yield(NULL);
                __usleep(1);
                goto write_again;
            } else if (timeout != 0 && t_diff <= timeout) {
                // Timeout이 세팅되어 있으면, 정해진 시간만큼 재시도
                // pth_yield(NULL);
                __usleep(1);
                goto write_again;
            } else {
                // 그외의 경우는 에러라고 판단.
                this->error = true; // FIXME: 왜 이것이 없을까?
                goto write_end;
            }
        } else {
            /* Is it normal or strange?? */
            assert(len_tmp > n_tmp);
            len_tmp -= n_tmp;

            // n바이트만큼 쓴 상황임.
            assert(len_tmp == len - n);

            pBuf = (char*) buf + n;

            int t_diff = (int) (time(NULL) - t0);

            // 2003-05-27 Write 실패시 timeout만큼 재시도 함.
            if (timeout == 0) {
                // Timeout이 0이면, 무한히 반복되는 한이 있더라도 재시도
                // pth_yield(NULL);
                __usleep(1);
                goto write_again;
            } else if (timeout != 0 && t_diff <= timeout) {
                // Timeout이 세팅되어 있으면, 정해진 시간만큼 재시도
                // pth_yield(NULL);
                __usleep(1);
                goto write_again;
            } else {
                // 그외의 경우는 에러라고 판단.
                this->error = true; // FIXME: 왜 이것이 없을까?
                goto write_end;
            }
        }
    } else {
        /* OK. Sent n bytes */
        assert(n == len);
    }

  write_end:

    return n;
}

void PthSocket::close()
{
    if (this->sockfd >= 0) {
        ::close(this->sockfd);
     // ::shutdown(this->sockfd, 2);
         this->sockfd = -1;
    }
}

char *PthSocket::peer_addr()
{
    return this->peer_name(); // FIXME: 메모리 리크가 있음.
}

string PthSocket::peeraddr()
{
    char buf[128];
    return string((char*) this->peer_name(buf));
}

typedef union _SockAddr {
    struct sockaddr s;
    struct sockaddr_in i;
} SockAddr_t;

string PthSocket::peername()
{
    char buf[128];
    return string(this->peer_name(buf));
}

// peername()으로 호출했으면 free를 해 줘야 하고,
// peername(buf) 로 호출 했으면 free해줄 필요가 없다.
char *PthSocket::peer_name(char *ipaddr_buf) // default = NULL
{
    // 특정 소켓에 연결된 상대방 호스트의 IP를 리턴한다.

    char *ipaddr = (ipaddr_buf == NULL) ?
                       (char *) malloc(32): ipaddr_buf;

    ipaddr[0] = '\0';

    SockAddr_t peer;
    SockLen peerlen; /* int peerlen; */
    peerlen = (sizeof(struct sockaddr) > sizeof(struct sockaddr_in)) ?
              sizeof(struct sockaddr): sizeof(struct sockaddr_in);

    int r = getpeername(sockfd, &(peer.s), (socklen_t*)&peerlen);
    if (r != 0) {
       if (
            errno == EBADF || /* Bad File Descriptor */
            errno == ECONNRESET || /* Connection reset by peer */
            errno == ENOTCONN ||   /* Transport endpoint is not connected */
            errno == ECONNABORTED || /* Software caused connection abort */
            errno == EINVAL || /* Invalid */
            errno == EIO || /* IO FAIL */
            errno == EPIPE || /* PIPE FAIL */
            0
          )
        {
             /* DO NOTHING */
        }

        return NULL;
    }

    strcpy(ipaddr, inet_ntoa(peer.i.sin_addr));

    return ipaddr;
}

int sock_get_port(SockAddr_t *sa)
{
    struct sockaddr_in *sin = (struct sockaddr_in *) sa;
    return(sin->sin_port);
}

int PthSocket::peerport()
{
    /* 특정 소켓에 연결된 상대방 호스트의 포트 번호를 리턴한다. */
    SockAddr_t peer;

    SockLen peerlen = (sizeof(struct sockaddr) > sizeof(struct sockaddr_in)) ?
              sizeof(struct sockaddr): sizeof(struct sockaddr_in);

    int r = getpeername(sockfd, &(peer.s), (socklen_t*)&peerlen);

    if (r != 0) {
        return 0;
    }

    int port = sock_get_port(&peer);

    return port;
}

int PthSocket::myport()
{
    /* 특정 소켓에 연결된 자기 자신의 포트 번호를 리턴한다. */
    SockAddr_t peer;

    SockLen peerlen = (sizeof(struct sockaddr) > sizeof(struct sockaddr_in)) ?
              sizeof(struct sockaddr): sizeof(struct sockaddr_in);

    int r = getsockname(sockfd, &(peer.s), (socklen_t*)&peerlen);

    if (r != 0) {
        return 0;
    }

    int port = sock_get_port(&peer);

    return port;
}

#ifdef PTHSOCKET_TEST

int main()
{
    PthSocket sock("wallstmarketnews.biz", 25, 100);
    if (sock.isError()) {
        DEBUG_PRINT("error: %s\n", sock.errstr);
    } else {
        DEBUG_PRINT("connect success\n");
    }
    return 0;
}

#endif // PTHSOCKET_TEST

#ifdef _PTHSOCKET_TEST
int main()
{
    int port = 9110;

    DEBUG_PRINT("new PthSocket(%d)\n", port);

    PthSocket *server_sock = new PthSocket(port);

    while (1) {
        PthSocket *client_sock = server_sock->accept(5);
        if (client_sock == NULL || client_sock->isError()) {
            DEBUG_PRINT("try accept again\n");
            // Pth::sleep(1);
            if (client_sock != NULL) { delete client_sock; }
            continue;
        }

        client_sock->write("WELCOME\n", 8);
        if (client_sock->isError()) {
            client_sock->close();
            delete client_sock;
            continue;
        }

        while (1) {
            char buf[BUFSIZ];
            int r = client_sock->readline(buf, 10);
            if (client_sock->isError()) {
                DEBUG_PRINT("timeout or socket_error\n");
                client_sock->close();
                break;
            }

            for (int i = 0; i < r; i++) {
                buf[i] = toupper(buf[i]);
            }

            client_sock->write(buf, r);
            if (client_sock->isError()) {
                client_sock->close();
                break;
            }

            if (strncmp(buf, "QUIT", 4) == 0) {
                client_sock->close();
                break;
            }
        }

        delete client_sock;
    }

    return 0;
}
#endif // PTHSOCKET_TEST

