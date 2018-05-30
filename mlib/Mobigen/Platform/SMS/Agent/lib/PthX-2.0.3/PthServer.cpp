#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <assert.h>
#include <signal.h>
#include <time.h>
#include <ctype.h>

#include <fcntl.h> // umask()
#include <sys/types.h> // wait()
#include <sys/wait.h> // wait()
#include <sys/stat.h> // stat()

#include <vector>
#include <string>
#include <algorithm>

#include <errno.h>

using namespace std;

#include "PthServer.h"

#ifndef DEBUG_PRINT
#  ifdef NDEBUG
#    define DEBUG_PRINT if (0) printf
#  else // NDEBUG
#    define DEBUG_PRINT printf("(%s,%d) ", __FILE__, __LINE__); printf
#  endif // NDEBUG
#endif // DEBUG_PRINT

time_t start_time = 0;

void MultiProc::set_check_period(int check_period)
{
        this->check_period = check_period;
}

void MultiProc::set_fork_delay(int fork_delay)
{
        this->fork_delay = fork_delay;
}

void MultiProc::set_max_children(int max_children)
{
        this->max_children = max_children;
}

void MultiProc::set_heartbeat(const string &key, int time)
{
    this->heartbeat_key = key;
    this->heartbeat_time = time;
}


// virtual
void MultiProc::before_loop() // DEFAULT handler
{
    DEBUG_PRINT("MultiProc::before_loop()\n");
}

// virtual
void MultiProc::init_child() // DEFAULT handler
{
    DEBUG_PRINT("MultiProc::init_child()\n");
}

// virtual
void MultiProc::main_service() // DEFAULT handler
{
    // DEBUG_PRINT("MultiProc::main_service()\n");
}

MultiProc::MultiProc()
{
    this->pid = getpid();
    this->max_children = 1;
    this->fork_delay = 1;
    this->check_period = 5;
    this->children = new vector<pid_t>;

    this->heartbeat_time = 60 * 10;
          // 10분 이상 heart-beat가 울리지 않으면
          // 죽은 프로세스로 간주한다.
    this->heartbeat_key = "pth_deamon";
}

MultiProc::~MultiProc()
{
    // DEBUG_PRINT("~MultiProc()\n");
    delete this->children;
}

static bool file_exists(const string &file)
{
    struct stat stbuf;
    return (stat(file.c_str(), &stbuf) == 0) ? true: false;
}

static time_t file_mtime(const string &file)
{
    struct stat stbuf;
    return (stat(file.c_str(), &stbuf) == 0) ? stbuf.st_mtime: 0;
}

static string INT2STRING(int i)
{
    char str[64]; sprintf(str, "%d", i); return str;
}

static void touch_heart_beat_pid(const string &key, int pid)
{
    static time_t last_touch_time = 0;

    // 2003/12/27 - 1분 이내에는 touch 하지 않도록 한다.
    if ((time(NULL) - last_touch_time) < 60) {
        // DEBUG_PRINT("pid:%d, touch heartbeat, delayed\n", pid);
        return;
    }

    last_touch_time = time(NULL);

    DEBUG_PRINT("pid:%d, touch heartbeat\n", pid);

    umask(0);
    if (! file_exists("/tmp/" + key)) {
        ::mkdir(("/tmp/"+key).c_str(), 0777);
        errno = 0;
    }

    FILE *fp = fopen(("/tmp/"+key+"/"+INT2STRING(pid)+".pid").c_str(),
                     "w+");
    if (fp != NULL) {
        fprintf(fp, "heart-beat: %d\n", (int)last_touch_time);
        fclose(fp);
    }
}

/*
static bool kill_check_alive(int pid)
{
    int kill_result = ::kill(pid, 0);
    bool is_alive = (kill_result == 0) ? true: false;
    return is_alive;
}
*/

static bool timeout_check_alive(const string &key, int pid,
                               int heartbeat_time)
{
    const string &filename = "/tmp/"+key+"/"+INT2STRING(pid)+".pid";
    time_t mtime = file_mtime(filename);

    DEBUG_PRINT("t_diff: %d, heartbeat_time: %d\n",
        (int)(time(NULL) - mtime), heartbeat_time);

    if (time(NULL) - mtime > heartbeat_time) {
        DEBUG_PRINT("heartbeat이 더이상 울리지 않음. 죽었음.\n");
        // 정해진 시간 보다 더 오랫동안,
        // queue/pid.pid파일이 touch되지 않았음.
        // 이 프로세스는 죽은 것으로 간주하여야 함.
        return false;
    }

    DEBUG_PRINT("heartbeat_pid:%d, mtime: %d\n", pid, (int) mtime);

    return true;
}

static void kill_proc(const string &key, int pid)
{
    ::kill(pid, SIGKILL);

    // 죽은 Processdml PID 파일은 삭제해서, 쓰레기가 남지 않도록 함.
    ::unlink(("/tmp/"+key+"/"+INT2STRING(pid)+".pid").c_str());
    errno = 0;
}

vector<pid_t> *children_alive(const string &key, int heartbeat_time,
                              vector<pid_t> *children_old)
{
    vector<pid_t> *children_live = new vector<pid_t>;

    for (int i = 0; i < (int) children_old->size(); i++) {
        pid_t pid = (*children_old)[i];

        int kill_result = ::kill(pid, 0);
        bool is_alive = (kill_result == 0) ? true: false;

        DEBUG_PRINT("pid:%d, kill_result:%d, is_alive:%d\n",
            (int)pid, kill_result, (int)is_alive);

        if (is_alive) {
            // 프로세스가 살아 있어도, heartbeat를 보고 다시 한번
            // 더 판단한 후에, 최종적으로 살아 있음을 판단한다.
            if (timeout_check_alive(key, pid, heartbeat_time)) {
                children_live->push_back(pid);
                continue;
            } else {
                DEBUG_PRINT("killing blocked process\n");
                kill_proc(key, pid);
            }
        } else {
            DEBUG_PRINT("pid: %d is dead.\n", (int) pid);
            ::unlink(("/tmp/"+key+"/"+INT2STRING(pid)+".pid").c_str());
            errno = 0;
        }
    }

    delete children_old;

    return children_live;
}

void DEBUG_print_children(vector<pid_t> *children_old)
{
    printf("CHILDREN: ");

    for (int i = 0; i < (int)children_old->size(); i++) {
        printf("%d ", (int) (*children_old)[i]);
    }

    printf("\n");
}

void MultiProc::start()
{
    PthSocket::set_rlimit_max();

    this->before_loop();

#ifdef __FreeBSD__
    signal(SIGCHLD, SIG_IGN);
#else
    signal(SIGCLD, SIG_IGN);
#endif
    signal(SIGPIPE, SIG_IGN);


    while (1) {
        this->children = children_alive(this->heartbeat_key,
                            this->heartbeat_time, this->children);

        // DEBUG_print_children(this->children);

        if ((int)this->max_children == 0 ||
            (int) this->children->size() < (int)this->max_children)
        {
            DEBUG_PRINT("restart a new process\n");

            // 몇 번의 child 호출을 해야 할 지를 결정한다.
            int n_new_child = (this->max_children == 0) ? 1:
                   (this->max_children - this->children->size());

            for (int ii = 0; ii < n_new_child; ii++) {
                // max_child == 0 일 경우는, fork() 없이, parent process 자신이
                // 직접 서비스를 수행하도록 한다. 
                pid_t c_pid = (this->max_children == 0) ? 0 : fork();

                if (c_pid == (pid_t) 0) {

                    start_time = time(NULL);

                    this->pid = getpid();

                    // 2004.10.18 smy
                    // touch heatbeat so that monitoring procedure knows
                    // that I'm alive.
                    touch_heart_beat_pid(this->heartbeat_key, getpid());

                    // 개개의 차일드 핸들러가 호출 되기 전에
                    // 수행되어야 할 핸들러 호출
                    this->init_child();

                    // 메인 서비스 핸들러를 호출해 준다.
                    this->main_service(); 

                    DEBUG_PRINT("main_service() done, process dies.\n");

                    exit(0); 
                }
                this->children->push_back(c_pid);
            }

            // 2003/04/18 - 여기서 wait할 필요 없음.
            //              fork한 프로세스들은 모두 끝나면 죽을 것이고,
            //             죽으면, SIGCHLD 를 내는데, 그 시그날은 무시됨.
            //             여기서 wait()하면, fork()된 모든 프로세스가 죽기
            //             전까지 새로운 프로세스를 살리지 않고 계속 
            //             기다리기만 함.
            // int wait_status;
            // wait(&wait_status);

            PthTask::sleep(this->fork_delay);
        } else {
            DEBUG_PRINT("don't restart new child, max:%d, cur:%d\n",
                 this->max_children, (int) this->children->size());
        }

        // 2004/01/09
        // max_service_per_child > 0 일 경우, 새로운 프로세스를 살려야할
        // 필요가 많을 때, 체크 기간이 너무 길면 잠깐 동안의 블락 현상이
        // 생길 수 있으므로, 체크 기간을 1초 이하로 줄인다.
        // PthTask::sleep(this->check_period);

        PthTask::usleep(this->check_period*100000);
    }
}

PthServer::PthServer()
{
    this->port = 0;
    this->listen_sock = NULL;

    this->max_threads = 0;           // 0 == no limit
    this->max_service_per_child = 0; // 0 == no limit
}

PthServer::~PthServer()
{
    if (this->listen_sock != NULL) {
        delete this->listen_sock;
    }
}

// virtual
void PthServer::before_loop()
{
    DEBUG_PRINT("new PthSocket(%d)\n", this->port);

    this->listen_sock = new PthSocket(this->port);
    if (this->listen_sock == NULL || this->listen_sock->error) {
        printf("new PthSocket(%d) failed\n", this->port);
        exit(0);
    }
}

#define CLOSE_DELETE(x) if ((x)!=NULL) {(x)->close(); delete (x); (x) = NULL;}

class ServiceThread: public PthTask
{
  public:
    PthServer *ThisServer; // don't delete this
    PthSocket *sock; 

  public:
    ServiceThread(PthServer *ThisServer, PthSocket *sock)
        : PthTask()
    {
        assert(ThisServer != NULL);
        assert(sock != NULL);

        this->ThisServer = ThisServer;
        this->sock = sock;
    }

    ~ServiceThread()
    {
        assert(this->sock != NULL);

        CLOSE_DELETE(this->sock);
    }

    void run()
    {
        this->ThisServer->service(sock);
    }
};

#if 1
// virtual
void PthServer::main_service()
{
    assert(this->listen_sock != NULL);

    int thread_count = 0;
    while (1) {
        // touch heatbeat so that monitoring procedure knows that I'm alive.
        touch_heart_beat_pid(this->heartbeat_key, getpid());

        if (this->max_threads > 0 &&
            PthTask::activeCount() >= this->max_threads)
        {
            PthTask::yield();
            // ----------------------------------------------------------
            // 2003/12/31 sleep(1) 최대 커넥션이 넘어가면, sleep(1)시키기
            // ----------------------------------------------------------
            PthTask::sleep(1);
            continue;
        }

        PthSocket *channel = this->listen_sock->accept(10);
        if (channel == NULL || channel->error) {
            if (channel != NULL) {
                delete channel;
            }
            // ----------------------------------------------------------
            // 2003/13/31 accept() fail나면 일단 다른 thread로 yield함.
            //            무한 루프를 방지하기 위해서...
            // ----------------------------------------------------------
            PthTask::yield();
            continue;
        }


        ServiceThread *thr = new ServiceThread(this, channel);
        if (thr == NULL) {
            DEBUG_PRINT("new ServiceThread() failed\n");
            assert(channel != NULL);
            delete channel;
            continue;
        }

        thr->set_auto_delete(true);
        thr->start();

        if (this->max_service_per_child > 0) {
            thread_count = (thread_count+1) % 100000;
            if (thread_count >= this->max_service_per_child) {
                DEBUG_PRINT("max_service_per_child\n");
                break;
            }
          #if 0
            else {
                DEBUG_PRINT("thread_count:%d < max_service_per_child:%d ***\n",
                    thread_count, this->max_service_per_child);
            }
          #endif
        }
    }

    if (this->max_service_per_child == 0) {
        DEBUG_PRINT("max_service_per_child equal zero\n");
        assert(0);
    }

    while (PthTask::activeCount() > 0) {
        PthTask::usleep(10000);
    }

  {
    this->listen_sock->close();
    delete this->listen_sock; 
    this->listen_sock = NULL;
  }
}
#endif // 0

// virtual
void PthServer::service(MSocket *sock) // Default Service Routine
{
    assert(sock != NULL);

    char *welcome = "+OK PthServer Welcome\r\n";
    sock->write(welcome, strlen(welcome));
    if (sock->isError()) {
        return;
    }

    while (1) {
        char buf[BUFSIZ];

        int r = sock->readline(buf, 30);
        if (sock->isError()) {
            DEBUG_PRINT("timeout or socket_error\n");
            break;
        }

        if (strncasecmp(buf, "quit", 4) == 0) {
            sock->write("+ QUIT\r\n", 8);
            break;
        }

        for (int i = 0; i < r; i++) {
            buf[i] = toupper(buf[i]);
        }

        sock->write("+OK ", 4);
        if (sock->isError()) {
            break;
        }

        sock->write(buf, r);
        if (sock->isError()) {
            break;
        }
    }
}

#ifdef PTHSERVER_TEST

class DummyPopServer: public PthServer {
  public:
    void service(MSocket *sock);
};

int global_count = 0;
int line_count = 0;

void DummyPopServer::service(MSocket *sock)
{
    assert(sock != NULL);

    char *welcome = "220 +OK MyPop Welcome\r\n";
    sock->write(welcome, strlen(welcome));
    if (sock->isError()) {
        DEBUG_PRINT("sock write failed\n");
        return;
    }

    while (1) {
        line_count++;
        char buf[BUFSIZ];
        errno = 0;
        sock->readline(buf, 10);
        if (sock->isError()) {
            DEBUG_PRINT("read timeout/error [%s]\n", strerror(errno));
            break;
        }

        if (strncasecmp(buf, "quit", 4) == 0) {
            sock->write("+ QUIT\r\n", 8);
            break;
        }

        if (strncasecmp(buf, "user", 4) == 0 ||
            strncasecmp(buf, "pass", 4) == 0 ||
            strncasecmp(buf, "list", 4) == 0 ||
            strncasecmp(buf, "uidl", 4) == 0 ||
            strncasecmp(buf, "rset", 4) == 0)
        {
            
            string ok = string("+ OK ") + buf;
            sock->write((char*)ok.c_str(), ok.size());
            if (sock->isError()) {
                break;
            }

            continue;
        }

        if (strncasecmp(buf, "retr", 4) == 0) {
            bool is_error = false;
            for (int i = 0; i < 100; i++) {
                char*x="01234567890123456789012345678901234567890123456789\r\n";
                sock->write(x, strlen(x));
                if (sock->isError()) {
                    is_error = true;
                }
            }

            if (! is_error) {
                sock->write(".\r\n", 3);
                if (sock->isError()) {
                    break;
                }
            }

            continue;
        }

        string error = string("-ERR UNKNOWN COMMAND ") + string(buf);
        sock->write((char*)error.c_str(), error.size());
        if (sock->isError()) {
            break;
        }
    }

    if (global_count++ % 2 == 0) {
       int t_diff = (int)time(NULL) - (int)start_time;
       DEBUG_PRINT("t: %d, pid:%d, global_cnt: %d, "
                   "line_cnt:%d, active:%d, thrpt:%3.2f\n",
         t_diff, (int)getpid(), global_count, line_count,
         PthTask::activeCount(), (float) global_count / (float)t_diff);
    }
}

class DummyEchoServer: public PthServer {
  public:
    void service(MSocket *sock);
};

void DummyEchoServer::service(MSocket *sock)
{
    assert(sock != NULL);

/*
DEBUG_PRINT("무한루프 시험\n");
while (1) {
     int a = 2;
     a = a % 3;
}
*/

    char *welcome = "220 +OK MyPop Welcome\r\n";
    sock->write(welcome, strlen(welcome));
    if (sock->isError()) {
        DEBUG_PRINT("sock write failed\n");
        return;
    }

    while (1) {
        line_count++;
        char buf[BUFSIZ];
        errno = 0;
        sock->readline(buf, 10);
        if (sock->isError()) {
            DEBUG_PRINT("read timeout/error [%s]\n", strerror(errno));
            break;
        }

        if (strncasecmp(buf, "QUIT", 4) == 0) {
            sock->write("+OK Close\r\n", 10);
            break;
        }

        string resp = string("+OK ") + string(buf);
        sock->write((char*)resp.c_str(), resp.size());
        if (sock->isError()) {
            break;
        }
    }

    if (global_count++ % 2 == 0) {
       int t_diff = (int)time(NULL) - (int)start_time;
       DEBUG_PRINT("t: %d, pid:%d, global_cnt: %d, "
                   "line_cnt:%d, active:%d, thrpt:%3.2f\n",
         t_diff, (int)getpid(), global_count, line_count,
         PthTask::activeCount(), (float) global_count / (float)t_diff);
    }
}

int main(int argc, char *argv[])
{
    if (argc < 2) {
        printf("Usage: %s portnum\n", argv[0]);
        exit(0);
    }

    int port = atoi(argv[1]);

    PthSocket::set_rlimit_max();

    DummyEchoServer serv;
    // DummyPopServer serv;
    // PthServer serv;

    serv.set_port(port);
    serv.set_max_children(0); // 0: single process, no monitoring process

    // serv.set_max_threads(0);
    // serv.set_max_service_per_child(3);

    serv.set_heartbeat("pth_daemon", 30);

    serv.start();
}

#endif // PTHSERVER_TEST
