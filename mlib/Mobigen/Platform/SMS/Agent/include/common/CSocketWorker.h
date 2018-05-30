// Definition of the Socket class

#ifndef Socket_class
#define Socket_class


#include <sys/types.h>
#include <sys/socket.h>
#include <sys/signal.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>
#include <string>
#include <arpa/inet.h>
#include <stdio.h>
#include <errno.h>
#include <time.h>

#define LISTEN_TCP			0x01
#define LISTEN_UDP			0x02
#define LISTEN_NONBLOCK		0x04

//! TCP/IP 소켓에 관련된 기능을 담당하는 클래스

class CSocketWorker
{
 public:
	 /** 생성자 */
  CSocketWorker();
	/** 소멸자 */
  virtual ~CSocketWorker();
  /**
   *	TCP/IP 소켓 초기화
   *	@return true if success, else return flase.
   */
  bool create();
  /**
   *	주어진 포트번호로 bind하는 메쏘드.
   *	@param socket listen port.
   *	@return true if sucess, else return false.
   */
  bool bind ( int port );
  /**
   *	Socket listen method.
   *	@return true if succss, else return false.
   */
  bool listen() ;
  /**
   *	Socket accept method.
   *	@return true if success, else return false.
   */
  bool accept ( );
  /**
   *	Socket session close method.
   *	@param socket descriptor.
   *	@return true if success, else return false.
   */
  bool close( int fd );
  /**
   *	Close client socket session method.
   */
  void close_cli(){ close(m_clisd); m_clisd = -1; }
  /**
   *	read data from socket session
   *	@param socket descriptor.
   *	@param data buffer.
   *	@param data buffer size.
   *	@param timeout(seconds).
   *	@return read bytes.
   */
  int readn(int fd, char *buf, int buf_len, int timeout);
  /**
   *	method to connect to remote host
   *	@param remote host domain name or ip address.
   *	@param connect port.
   *	@return true if success, else return false.
   */
  bool connect ( std::string host, int port );
  /**
   *	send data to socket session
   *	@param send message
   *	@return true if success, else return false
   */
  bool sendMsg ( std::string );
  /**
   *	recieve data from socket session
   *	@param data buffer.
   *	@return recieve count
   */
  int recvMsg ( std::string& buf) ;
  /**
   *	method for setting blocking mode to socket session.
   *	@param true : block mode, false : non block mode.
   */
  void set_non_blocking ( bool b);
  /**
   *	method for check if socket session is valid.
   *	@return true if socket session is valid, else return false.
   */
  bool is_valid() { return m_sd != -1; }
  /**
   *	method to connect socket session.
   */
  void connectProcess();
  /**
   *	method for getting socket descriptor.
   *	@return socket descriptor.
   */
  int getFD();
  /**
   *	method for getting client socket descriptor.
   *	@return client socket descriptor(client socket session)
   */
  int getClientSD(){ return m_clisd; }

 private:

  int m_sd;	/**< socket descriptor */
  int m_clisd;	/**< client socket descriptor(client socket session) */
  /**
   *	socket error method.
   *	@param socket error number.
   *	@return errno.
   */
  int softerror(int err);
  /**
   *	method for setting host addresss to sockaddr_in structure.
   *	@param sockaddr_in structure.
   *	@param host address.
   *	@return 0 if success, else return < 0.
   */
  int setAddress(struct sockaddr_in *addr, const char *host);

 protected:
  sockaddr_in m_addr;	/**< sockaddr_in structure */

};


#endif


