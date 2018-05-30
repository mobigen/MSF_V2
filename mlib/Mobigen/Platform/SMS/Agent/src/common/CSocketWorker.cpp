// Implementation of the CSocketWorker class.


#include "CSocketWorker.h"
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <iostream>
#include <sys/time.h>



CSocketWorker::CSocketWorker() :
	m_sd ( -1 )
{

	memset (&m_addr, 0, sizeof(m_addr));

}

CSocketWorker::~CSocketWorker()
{
	if ( is_valid() )
	  ::close ( m_sd );
}

int CSocketWorker::softerror(int num){
    switch (num) {
    case EAGAIN:
    case ENOSR:
    case ENODEV:
    case ENOSPC:
    case ENOMEM:
    case ENXIO:
    case ENOBUFS:
    case EINTR:
        return(1);

    default:
        return(0);
    }
}


bool CSocketWorker::create()
{
	m_sd = socket ( AF_INET,
		    SOCK_STREAM,
		    0 );

	if ( ! is_valid() )
	  return false;


	// TIME_WAIT - argh
	int on = 1;
	if ( setsockopt ( m_sd, SOL_SOCKET, SO_REUSEADDR, ( const char* ) &on, sizeof ( on ) ) == -1 )
	  return false;


	return true;

}



bool CSocketWorker::bind ( int port )
{

	if ( ! is_valid() )
	  {
	    return false;
	  }



	m_addr.sin_family = AF_INET;
	m_addr.sin_addr.s_addr = INADDR_ANY;
	m_addr.sin_port = htons ( port );

	int bind_return = ::bind ( m_sd,
			     ( struct sockaddr * ) &m_addr,
			     sizeof ( m_addr ) );


	if ( bind_return == -1 )
	  {
	    return false;
	  }

	return true;
}


bool CSocketWorker::listen() 
{
	if ( ! is_valid() ) return false;

	if((::listen ( m_sd, 1 ))== -1)
	{
		return false;
	}

	return true;
}


bool CSocketWorker::accept ( )
{
	int addr_length = sizeof ( m_addr );
	fd_set	rset, allset;
	struct timeval tv;

	for(;;){
	  FD_ZERO(&allset);
	  FD_SET(m_sd, &allset);
	  memset(&tv, 0x00, sizeof(tv));
	  tv.tv_sec=1;
	  tv.tv_usec=0;
	  rset = allset;
	
	  if(select(m_sd+1, &rset, NULL, NULL, &tv)<=0)
		continue;
	
	  if(FD_ISSET(m_sd, &rset)){
		  m_clisd =
//#ifdef HPUX 11.11에서는 컴파일 되도록 수정함. gcc 4.1.1
//			::accept (m_sd, (sockaddr *) &m_addr, (int *) &addr_length );
//#else
			::accept (m_sd, (sockaddr *) &m_addr, (socklen_t *) &addr_length );
//#endif
		  if ( m_clisd <= 0 ){
			fprintf(stderr,"Error: in CSocketWorker::accept() Failed [errno:%s]\n",
				strerror(errno));
		    return false;
		  }
		  else
		    return true;
	  }
	}
}


bool CSocketWorker::sendMsg ( std::string s ) 
{
	int length = s.length(), totalcount=0, packetCount=0, i=0;

	if((::write ( m_sd, s.c_str(), length)) == -1) {
		fprintf(stderr, "[%s,%d] error [%s]\n", __FUNCTION__, __LINE__, strerror(errno));
		return false;
	} else {
		    return true;
	}
}

int CSocketWorker::recvMsg ( std::string& s ) 
{
	int len = 0;
	char buf[1024];
	memset(buf, 0x00, sizeof(buf));
	if ((len = readn(m_sd, buf, sizeof(buf)-1, 1)) <= 0)
	{
		return -1;
	}

	return len;
}

bool CSocketWorker::connect(std::string host, int port)
{
	int err=-1;
	struct sockaddr_in sa;

	if((m_sd=socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0)
		goto RETURN_OUT;

	sa.sin_family = AF_INET;
	err = setAddress(&sa, host.c_str());
	sa.sin_port = htons((unsigned short int)port);

	if((err=::connect(m_sd, (struct sockaddr*)&sa, sizeof(sa)))<0){
		if(errno==EINPROGRESS || errno==EINTR || errno==EALREADY)
			err=0;
	}else
		err=0;

RETURN_OUT:
	if(err){
		close(m_sd);
		return false;
	}else
		return true;
}

bool CSocketWorker::close(int fd)
{
	if( ! is_valid() ) return false;
	int status = ::close ( fd );
	if(status == 0)
		return true;
	else{
		fprintf(stderr,"Error: socket close failed[errno:%s]\n", strerror(errno));
		return false;
	}
}

void CSocketWorker::set_non_blocking ( bool b )
{

	int opts;

	opts = fcntl ( m_sd, F_GETFL );

	if ( opts < 0 )
	{
	    return;
	}

	if ( b )
	  opts = ( opts | O_NONBLOCK );
	else
	  opts = ( opts & ~O_NONBLOCK );

	fcntl ( m_sd, F_SETFL,opts );
}

int CSocketWorker::getFD()
{
	return m_sd;
}

int CSocketWorker::setAddress(struct sockaddr_in *sa, const char *addr)
{
	unsigned long inaddr;
	struct hostent *p;
	if((inaddr = inet_addr(addr)) != -1){
	}else {
		if((p=gethostbyname(addr)) == NULL) {
			return -1;
		}else {
			memcpy(&sa->sin_addr, p->h_addr_list[0], p->h_length);
		}
	}
	return 0;
}

/*************
void CSocketWorker::connectProcess()
{
	proto_header header;

	memset(&header, 0x00, sizeof(header));
	struct timespec interval, remainder;
	interval.tv_sec=0;
	interval.tv_nsec=10000000; 
	if (nanosleep(&interval, &remainder) == -1) {
		if (errno == EINTR) {
			//fprintf(stderr,"[%s][%d] nanosleep interrupted\n",__FILE__,__LINE__);
		}
		else fprintf(stderr,"nanosleep");
	}
}
******************/

int CSocketWorker::readn(int fd, char *ptr, int nbytes, int timeout)
{
    int nleft, nread,cnt=0;
    struct timeval  tv;
    fd_set          rfds;

    tv.tv_sec=timeout;
    tv.tv_usec=0;

    nleft = nbytes;
    while (nleft > 0)
    {
        while(1)
        {
            FD_ZERO(&rfds);
            FD_SET(fd,&rfds);
            if(select(fd+1,&rfds,NULL,NULL,&tv) < 0)
            {
                if(errno == EINTR)
                {
                    continue;
                } else
                    return(-1);
            } else
                break;
        }
        if(!FD_ISSET(fd,&rfds))
        {
            return(nbytes - nleft);     /* return >= 0 */
        /*  return (-2); */
        }
        nread = read(fd, ptr, nleft);

        tv.tv_sec=timeout;
        tv.tv_usec=0;


        if (nread < 0) {
            if (!softerror(errno))
                    return(-1);
            else
                    continue;
        } else if (nread == 0)
            break;          /* EOF */

        /*
        if (cnt > 3) break;
        */

        nleft -= nread;
        ptr   += nread;
    }

    return(nbytes - nleft);     /* return >= 0 */
}

void CSocketWorker::connectProcess()
{
	return ;
}
