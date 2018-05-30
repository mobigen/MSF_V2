#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <assert.h>
#include <errno.h>
#include <sys/poll.h>

#include <sys/time.h>
#include <time.h>

#include <string>
using namespace std;

#include "StrUtil.h"
#include "MD5.h"
#include "PthTask.h"
#include "SecureProxy.h"

#ifndef DEBUG_PRINT
#  ifdef NDEBUG
#    define DEBUG_PRINT if (0) printf
#  else
#    define DEBUG_PRINT printf("(%s,%d) ", __FILE__, __LINE__); printf
#  endif // NDEBUG
#endif // DEBUG_PRINT

string bin2hex(const string &str)
{
    string hex = "";

//  DEBUG_PRINT("bin2hex: '%s' => \n", str.c_str());

    for (int i = 0, n = str.size(); i < n; i++) {
        char hex_char[32];
        sprintf(hex_char, "%02x", (unsigned char) str[i]);
        hex += hex_char;
    }

//  DEBUG_PRINT("bin2hex: '%s'\n", hex.c_str());

    return hex;
}

string hex2bin(const string &str)
{
    string bin = "";

//  DEBUG_PRINT("hex2bin: '%s' => \n", str.c_str());

    for (int i = 0, n = str.size(); i < n; i += 2) {
        string hex = str.substr(i, 2);
        unsigned int c;
        sscanf(hex.c_str(), "%02x", &c);
        bin += (char)c;
    }

//  DEBUG_PRINT("hex2bin: '%s'\n", bin.c_str());

    return bin;
}

static const char *B32 = "0123456789abcdefghijklmnopqrstuv";
// #define B32_VAL(x) (int)(strchr(B32,(x)) - B32)
#define B32_VAL(x) (((x) <= '9') ? ((int)((x)-'0')): ((int)((x)-'a')+10))

// private
string ProxyChannel::encrypt(const string &line)
{
    // key가 비어 있으면, 암호화 하지 않고, 원문을 그대로 전송한다.
    if (this->key == "") {
        return line;
    }

    string hex = bin2hex(StrUtil::trim_blanks(line));

    string encrypted = "";
    for (int i = 0, n = hex.length(); i < n; i++) {
        encrypted += B32[B32_VAL(hex[i]) + B32_VAL(this->key[i%32])];
    }

// DEBUG_PRINT("encrypted: %s\n", encrypted.c_str());

    return encrypted + "\n";
}

// private
string ProxyChannel::decrypt(const string &line)
{
    // key가 비어 있으면, 암호화 하지 않고, 원문을 그대로 전송한다.
    if (this->key == "") {
        return line;
    }

    string hex = "";
    for (int i = 0, n = line.length(); i < n; i++) {
        if (line[i] == '\n' || line[i] == '\r') { break; }
        hex += B32[B32_VAL(line[i]) - B32_VAL(this->key[i%32])];
    }

    string decrypted = hex2bin(hex);

    if (decrypted.c_str()[decrypted.length()-1] != '\n') {
        decrypted += '\n';
    }

    return decrypted;
}

ProxyChannel::ProxyChannel(PthSocket *s_sock, PthSocket *t_sock,
                             const string &key)
{
    assert(s_sock != NULL);
    assert(t_sock != NULL);

    this->s_sock = s_sock;
    this->t_sock = t_sock;
    this->key = key;

    DEBUG_PRINT("ProxyChannel::ProxyChannel(s_sck,t_sck,'%s')\n", key.c_str());
}

ProxyChannel::~ProxyChannel()
{
    if (this->s_sock != NULL) {
        this->s_sock->close();
        this->s_sock = NULL;
    }

    if (this->t_sock != NULL) {
        this->t_sock->close();
        this->t_sock = NULL;
    }

    DEBUG_PRINT("ProxyChannel::~ProxyChannel()\n");
}

void ProxyChannel::run()
{
    assert(this->s_sock != NULL);
    assert(this->t_sock != NULL);

    DEBUG_PRINT("ProxyChannel started.\n");

    struct timeval tv;

    fd_set rfds;
    fd_set wfds;
    fd_set efds;

    int largest_fd = this->s_sock->getSockFd();
    if (largest_fd < this->t_sock->getSockFd()) {
        largest_fd = this->t_sock->getSockFd();
    }

    string s_buf;
    string t_buf;

    while (true) {
        errno = 0;

        // DEBUG_PRINT("select wait...\n");

if (1) {
        FD_ZERO(&rfds);
        FD_ZERO(&wfds);
        FD_ZERO(&efds);
        FD_SET(this->s_sock->getSockFd(), &rfds);
        FD_SET(this->t_sock->getSockFd(), &rfds);
        FD_SET(this->s_sock->getSockFd(), &efds);
        FD_SET(this->t_sock->getSockFd(), &efds);

        tv.tv_sec = 870000;
        tv.tv_usec = 0;
}

        int r = ::select(largest_fd+1, &rfds, &wfds, &efds, &tv); // WAIT

        if (FD_ISSET(this->s_sock->getSockFd(), &efds)) { break; }
        if (FD_ISSET(this->t_sock->getSockFd(), &efds)) { break; }
        if (r == 0 && errno == 0) { break; }

        if (FD_ISSET(this->s_sock->getSockFd(), &rfds)) {
            char buf[BUFSIZ]; memset(buf, 0x00, BUFSIZ);
            errno = 0;

            r = this->s_sock->read(buf, BUFSIZ-1);

            if (this->s_sock->isError()) { break; }
            if (r == 0) { break; }
            if (r < 0 && errno != EAGAIN) { break; }

            s_buf += buf;

            char *p = strchr(s_buf.c_str(), '\n');
            while (p != NULL) {
                string read_line = s_buf.substr(0, p-s_buf.c_str()+1);
                string line = this->decrypt(read_line);

                // line contains '\r\n'

                this->t_sock->write(line.c_str(), line.length());
                if (this->t_sock->isError()) { break; }

                s_buf = s_buf.substr(p-s_buf.c_str()+1);
                p = strchr(s_buf.c_str(), '\n');
           }
        }

        if (FD_ISSET(this->t_sock->getSockFd(), &rfds)) {
            char buf[BUFSIZ]; memset(buf, 0x00, BUFSIZ);
            errno = 0;

            r = this->t_sock->read(buf, BUFSIZ-1);
            if (this->t_sock->isError()) { break; }
            if (r == 0) { break; }
            if (r < 0 && errno != EAGAIN) { break; }

            t_buf += buf;

            char *p = strchr(t_buf.c_str(), '\n');
            while (p != NULL) {
                string read_line = t_buf.substr(0, p-t_buf.c_str()+1);
                string line = this->encrypt(read_line);

                this->s_sock->write_line(line);
                if (this->s_sock->isError()) { break; }

                t_buf = t_buf.substr(p-t_buf.c_str()+1);
                p = strchr(t_buf.c_str(), '\n');
           }
        }
    }

    if (this->s_sock != NULL) {
        DEBUG_PRINT("close s_sock\n");
        this->s_sock->close();
        delete this->s_sock;
        this->s_sock = NULL;
    }

    if (this->t_sock != NULL) {
        DEBUG_PRINT("close t_sock\n");
        this->t_sock->close();
        delete this->t_sock;
        this->t_sock = NULL;
    }
}

// {

SecureProxyServer::SecureProxyServer(int s_port, const string &t_ip,
                                     int t_port, const string &shared_key)
{
    this->s_port = s_port;
    this->t_ip = t_ip;
    this->t_port = t_port;
    this->shared_key = shared_key;
}

SecureProxyServer::~SecureProxyServer()
{
    // do nothing?
}

// private
string SecureProxyServer::CRAM_MD5_server(PthSocket *s_sock)
{
    assert(s_sock != NULL);

    // shared_key 가 주어 지지 않으면, Challenge/Response 체크를 하지
    // 않고 원문 그대로 통신한다.
    if (this->shared_key == "") {
        DEBUG_PRINT("No encryption.\n");
        return "";
    }

    string challenge = MD5::encode(StrUtil::int2string(time(NULL)));
    s_sock->write_line("+OK SecureProxy: " + challenge + "\r\n");
    if (s_sock->isError()) {
        DEBUG_PRINT("CRAM_MD5_FAIL: s_sock->write_line() fail 1.\n");
        return "CRAM_MD5_FAIL";
    }

    DEBUG_PRINT("+OK WELCOME-SECURE-PROXY: %s\n", challenge.c_str());

    string resp = s_sock->read_line();
    if (s_sock->isError()) {
        DEBUG_PRINT("CRAM_MD5_FAIL: s_sock->read_line() fail\n");
        return "CRAM_MD5_FAIL";
    }

    resp = StrUtil::trim_blanks(resp);

    DEBUG_PRINT("resp: %s\n", resp.c_str());

    string right = MD5::encode(challenge+this->shared_key);
    if (resp != right) {
        s_sock->write_line("-ERR Mismatch. Not authorized.\r\n");
        DEBUG_PRINT("-ERR Mismatch: %s\n", resp.c_str());
        return "CRAM_MD5_FAIL";
    }

    DEBUG_PRINT("write_line(+OK Authorized\r\n");

    s_sock->write_line("+OK Authorized.\r\n");
    DEBUG_PRINT("+OK Authorized.\n");

    return MD5::encode(challenge+resp+this->shared_key);
}

void SecureProxyServer::run()
{
    PthSocket *server_sock = new PthSocket(this->s_port);
    if (server_sock->isError()) {
        DEBUG_PRINT("new ServerSocket(%d) failed\n", this->s_port);
        delete server_sock;
        return;
    }

    DEBUG_PRINT("listening secure port '%d'...\n", this->s_port);

    while (true) {
        PthSocket *s_sock = server_sock->accept();
		if (s_sock == NULL) {
            PthTask::usleep(1);
            continue;
		}

        if (s_sock->isError()) {
            delete s_sock;
            PthTask::usleep(1);
            continue;
        }

        DEBUG_PRINT("sock accepted. from: '%s'\n", s_sock->peeraddr().c_str());

        string key = this->CRAM_MD5_server(s_sock);
        if (key == "CRAM_MD5_FAIL") {
            s_sock->close(); delete s_sock;
            PthTask::usleep(1);
            continue;
        }

        DEBUG_PRINT("CRAM_MD5 success.\n");

        PthSocket *t_sock = new PthSocket(this->t_ip, this->t_port);
        if (t_sock->isError()) {
            t_sock->close(); delete t_sock;
            s_sock->close(); delete s_sock;
            PthTask::usleep(1);
            continue;
        }

        DEBUG_PRINT("connected: text_port '%s:%d'.\n",
            this->t_ip.c_str(), this->t_port);

        ProxyChannel *channel = new ProxyChannel(s_sock, t_sock, key);
        channel->set_auto_delete(true);
        channel->start();

        PthTask::usleep(1);
    }
}

// }

// {

SecureProxyClient::SecureProxyClient(int t_port, const string &s_ip,
                                     int s_port, const string &shared_key)
{
    this->t_port = t_port;
    this->s_ip = s_ip;
    this->s_port = s_port;
    this->shared_key = shared_key;
}

SecureProxyClient::~SecureProxyClient()
{
    // do nothing?
}

// private
string SecureProxyClient::CRAM_MD5_client(PthSocket *s_sock)
{
    assert(s_sock != NULL);

    // shared_key 가 주어 지지 않으면, Challenge/Response 체크를 하지
    // 않고 원문 그대로 통신한다.
    if (this->shared_key == "") {
        DEBUG_PRINT("No shared key. no encryption\n");
        return "";
    }

    // 우선 Welcome라인을 읽는다.
    string welcome = s_sock->read_line();
    if (s_sock->isError()) {
        DEBUG_PRINT("CRAM_MD5_FAIL: s_sock->read() fail 1.\n");
        return "CRAM_MD5_FAIL";
    }

    DEBUG_PRINT("WELCOME: %s\n", welcome.c_str());

    // Welcome라인에서, Challenge String을 뽑아낸다.
    vector<string> welcome_challenge = StrUtil::split(welcome, ": ");
    if (welcome_challenge.size() != 2) {
        DEBUG_PRINT("welcome line broken[%s]\n", welcome.c_str());
        return "CRAM_MD5_FAIL";
    }
    string challenge = StrUtil::trim_blanks(welcome_challenge[1]);

    DEBUG_PRINT("challenge: %s\n", challenge.c_str());

    // 뽑아낸 Challenge 스트링과 비밀번호를 이용해서 Response를 만든다.
    string resp = MD5::encode(challenge+this->shared_key);

    DEBUG_PRINT("resp: %s\n", resp.c_str());

    // Response를 전송한다.
    s_sock->write_line(resp + "\r\n");
    if (s_sock->isError()) {
        DEBUG_PRINT("CRAM_MD5_FAIL: s_sock->write() fail\n");
        return "CRAM_MD5_FAIL";
    }

    DEBUG_PRINT("s_sock->write_line(%s)\n", resp.c_str());

    DEBUG_PRINT("waiting +OK/-ERR...\n");

    // +OK 를 받는다.
    string ok = s_sock->read_line();
    if (s_sock->isError()) {
        DEBUG_PRINT("CRAM_MD5_FAIL: s_sock->read() fail 1.\n");
        return "CRAM_MD5_FAIL";
    }
    if (! StrUtil::startsWith(ok, "+OK ")) {
        DEBUG_PRINT("%s", ok.c_str());
        return "CRAM_MD5_FAIL";
    }

    // +OK를 받으면, challenge+resp+shared_key 를 묶어서 key를 생성한 후
    // 리턴한다.

    DEBUG_PRINT("+OK\n");

    return MD5::encode(challenge+resp+this->shared_key);
}

void SecureProxyClient::run()
{
    PthSocket *server_sock = new PthSocket(this->t_port);
    if (server_sock->isError()) {
        DEBUG_PRINT("new ServerSocket(%d) failed\n", this->t_port);
        delete server_sock;
        return;
    }

    DEBUG_PRINT("listening text port '%d'...\n", this->t_port);

    while (true) {
        PthSocket *t_sock = server_sock->accept();
        if (t_sock->isError()) {
            delete t_sock;
            PthTask::usleep(1);
            continue;
        }

        DEBUG_PRINT("accept from: '%s'\n", t_sock->peeraddr().c_str());

        PthSocket *s_sock = new PthSocket(this->s_ip, this->s_port);
        if (s_sock->isError()) {
            t_sock->close(); delete t_sock;
            s_sock->close(); delete s_sock;
            PthTask::usleep(1);
            continue;
        }

        DEBUG_PRINT("connect secure port: '%s:%d'\n", s_ip.c_str(), s_port);

        string key = this->CRAM_MD5_client(s_sock);
        if (key == "CRAM_MD5_FAIL") {
            s_sock->close(); delete s_sock;
            t_sock->close(); delete t_sock;
            PthTask::usleep(1);
            continue;
        }

        DEBUG_PRINT("CRAM_MD5 success.\n");

        ProxyChannel *channel = new ProxyChannel(s_sock, t_sock, key);
        channel->set_auto_delete(true);
        channel->start();

        PthTask::usleep(1);
    }
}

// }
