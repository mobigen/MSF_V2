#ifndef __PthMsg_c__
#define __PthMsg_c__
// ---------------------------------------------------------------------------
// PthMsg.cpp --
//   Timeout을 지원하는 SystemV IPC인 MsgQ의 구현.
//   Blocking되지 않는 것을 보장함.
//
// Updates:
//   2003/03/02 initially created.
// ---------------------------------------------------------------------------
#include "PthTask.h"

#include <stdio.h>
#include <sys/msg.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>
#include <unistd.h>

#include <string>
#include <cassert>

using namespace std;

#include "PthMsg.h"

#ifndef DEBUG_PRINT
#  ifdef NDEBUG
#    define DEBUG_PRINT if (0) printf
#  else // NDEBUG
#    define DEBUG_PRINT printf("(%s,%d) ", __FILE__, __LINE__); printf
#  endif // NDEBUG
#endif // DEBUG_PRINT

typedef struct _msg {
    long int type;
    char data[BUFSIZ];
} MyMsgType;

bool PthMsg::init(int key /* default = 129 */)
{
    this->error = false;
    this->errstr = "";

    errno = 0;
    this->qid = ::msgget((key_t) key, 0777|IPC_CREAT);
    if (this->qid >= 0) { // success;
        // DEBUG_PRINT("qid: %d, successfully made.\n", this->qid);
        return true;
    }

    this->error = true;
    this->errstr = strerror(errno);

    fprintf(stderr, "(%s,%d)::msgget(): %d:%s\n",
            __FILE__, __LINE__, errno, strerror(errno));

    DEBUG_PRINT("::msgget(): %d:%s\n", errno, strerror(errno));

    return false;
}

bool PthMsg::isError()
{
    return this->error;
}

PthMsg::PthMsg(int key /* default = 129 */)
{
    this->init(key);
}

PthMsg::~PthMsg()
{
    // do nothing
}

bool PthMsg::send(long int type, const string &str, int timeout)
{
    // DEBUG_PRINT("send(%d,%d)\n", this->qid, (int)type);

    assert(this->qid >= 0);
    assert(str.size() < BUFSIZ);

    if (this->error) {
        return false;
    }

    MyMsgType msg;

    msg.type = type;
    strcpy(msg.data, str.c_str());

    if (timeout == 0) {
        errno = 0;
        int r = ::msgsnd(this->qid, (void*) &msg, str.size()+1, 0);

        if (r >= 0) { // success, size of sent message ??
            this->error = false;
            return true;
        }

        if (r == -1) {
            this->error = true;
            this->errstr = strerror(errno);
            DEBUG_PRINT("%d: %s\n", errno, strerror(errno));
            return false;
        }

        assert(0); // r == 0 또는 r == -1만 허용 되는데...
    }

    assert(timeout > 0);

    time_t t0 = time(NULL);
    while (1) {
        int r = ::msgsnd(this->qid, (void*) &msg, str.size()+1, IPC_NOWAIT);

        if (r >= 0) { // send success, size of sent message ??
            this->error = false;
            return false;
        }

        if (r == -1) {
            if (errno == EAGAIN) {
                PthTask::yield();
                time_t t1 = time(NULL);
                if ((t1-t0) >= timeout) {
                    this->error = true;
                    this->errstr = "TIMEOUT";
                    DEBUG_PRINT("TIMEOUT\n");
                    return false;
                }
            } else {
                this->error = true;
                this->errstr = strerror(errno);
                DEBUG_PRINT("%s\n", strerror(errno));
                break;
            }
        }

        assert(0); // 결과는 항상 0 또는 -1이어야 함.
    }

    return true;
}

bool PthMsg::recv(long int type, string &str, int timeout)
{
    // DEBUG_PRINT("recv(%d,%d)\n", this->qid, (int) type);

    assert(this->qid >= 0);

    if (this->error) {
        return false;
    }

    MyMsgType msg;

    if (timeout == 0) {
        int r = ::msgrcv(this->qid, (void*) &msg, BUFSIZ, type, 0);

        if (r >= 0) { // success, size of received message?
            this->error = false;
            str = msg.data;
            // DEBUG_PRINT("r:%d, str.c_str():%s\n", r, str.c_str());
            return true;
        }

        if (r == -1) {
            this->error = true;
            this->errstr = strerror(errno);
            str = "";
            DEBUG_PRINT("%s\n", strerror(errno));
            return false;
        }

        DEBUG_PRINT("r=%d, errno=%d, %s\n", r, errno, strerror(errno));

        assert(0); // r == 0 또는 r == -1만 허용 되는데...
    }

    assert(timeout > 0);

    time_t t0 = time(NULL);
    while (1) {
        int r = ::msgrcv(this->qid, (void*) &msg, BUFSIZ, type, IPC_NOWAIT);

        if (r >= 0) { // send success, size of sent message ??
            this->error = false;
            int str_len = strlen(str.c_str());
            assert(str_len < BUFSIZ);
            str = str.substr(0, str_len);
            return false;
        }

        if (r == -1) {
            if (errno == EAGAIN) {
                PthTask::yield();
                time_t t1 = time(NULL);
                if ((t1-t0) >= timeout) {
                    this->error = true;
                    this->errstr = "TIMEOUT";
                    DEBUG_PRINT("TIMEOUT\n");
                    return false;
                }
            } else {
                this->error = true;
                this->errstr = strerror(errno);
                DEBUG_PRINT("%s\n", strerror(errno));
                break;
            }
        }

        assert(0); // 결과는 항상 0 또는 -1이어야 함.
    }

    return true;
}

bool PthMsg::remove()
{
    assert(this->qid >= 0);

    if (this->error) {
        return false;
    }

    errno = 0;
    ::msgctl(this->qid, IPC_RMID, NULL);

    if (errno != 0) {
        DEBUG_PRINT("msgctl(%d, IPC_RMID): %s\n", this->qid, strerror(errno));
        return false;
    }

    return true;
}

#ifdef PTH_MSG_TEST

void test_0()
{
    printf("test_0() - "); fflush(stdout);

    int key = 1010;

    if (fork() == 0) {
        // child
        PthMsg msgq(key);
        msgq.send(1, "한글 입력");
        // DEBUG_PRINT("msg sent: %d:%s\n", errno, strerror(errno));
        exit(0);
    }

    PthMsg msgq(key);
    string str;
    msgq.recv(1, str);
    // DEBUG_PRINT("msg recv: %d:%s\n", errno, strerror(errno));

    if (str != "한글 입력") {
        DEBUG_PRINT("str.c_str():%s, str.size():%d\n", str.c_str(), str.size());
    }
    assert(str == "한글 입력");

    printf("ok.\n");
}

string int2string(int ii)
{
    char str[128];
    sprintf(str, "%d", ii);
    return string(str);
}

/*
void test_1()
{
    printf("test_1() - "); fflush(stdout);

    int REQ_TYPE = 1;
    int NUM_TRIAL = 100;
    int key = 1010;

    if (fork() == 0) {
        // child
        PthMsg msgq(key);

        for (int i = 0; i < NUM_TRIAL; i++) {
            string str;
            msgq.recv(REQ_TYPE, str); // 메시지를 받아서...
            if (msgq.isError()) {
                DEBUG_PRINT("msgq.recv() failed\n");
            }
            assert(! msgq.isError());

            // str = "req_id 공백 request_string";
            int req_id = atoi(str.c_str());
            char *p = strchr(str.c_str(), ' ');
            assert(p != NULL);
            p++;
            char *msg_msg = p;
            for (int j = 0; *p != '\0'; j++, p++) {
                *p = ::toupper(*p);
            }

            msgq.send(req_id, msg_msg); 
            // DEBUG_PRINT("msg sent: %d:%s\n", errno, strerror(errno));
        }

        exit(0);
    }

    PthMsg msgq(key);

    for (int i = 0; i < NUM_TRIAL; i++) {
        int req_id = i+100;
        string req_msg = "xyz";
        string request = int2string(req_id) + " " + req_msg; 
        msgq.send(1, request);

        string str;
        msgq.recv(req_id, str);

        if (str != "XYZ") {
            DEBUG_PRINT("str.c_str():%s\n", str.c_str());
        }
        assert(str != "XYZ");
    }

    printf("ok.\n");
}
*/


int main()
{
    test_0();
//  test_1();

    return 0;
}

#endif // PTH_MSG_TEST

#endif // __PthMsg_c__
