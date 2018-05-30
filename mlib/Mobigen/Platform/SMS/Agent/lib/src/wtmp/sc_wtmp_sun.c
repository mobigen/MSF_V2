

#include <arpa/inet.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <netdb.h>
#include <stdio.h>
#include <signal.h>
#include <stdlib.h>
#include <string.h>
#include <stropts.h> // ¡÷¿« <sys/stropts.h>
#include <stdio.h>
#include <unistd.h>
#include <utmp.h>
#include <utmpx.h>
#include <dirent.h>

#include <sys/poll.h>
#include <sys/syslog.h>
#include <sys/strlog.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/utsname.h>

#define NINLOGS		10		/* max number of inputs */
#define	MAXLINE		1024	/* maximum line length */

#define LOG_FAC(p)	(((p) & LOG_FACMASK) >> 3)
#define LOG_PRI(p)	((p) & LOG_PRIMASK)

#define ERROR       3
#define WARNING     2
#define INFORMATION 1

static	int	 g_in = 0;	/* number of inputs */

static	struct pollfd g_pollfd[NINLOGS];
static	char   *LogName = "/dev/log";

extern	int  errno;
extern	char *ctime();

int g_wtmpfd;

void  monitor_wtmp(); 
void  freelog ( );
void  *monitor_log();

int init()
{
	int funix;
	struct utsname up;
	struct strioctl str;

    if((g_wtmpfd=open( WTMPX_FILE, O_RDONLY ))<0)
		return -1;

    if (lseek(g_wtmpfd, 0, SEEK_END) < 0) {
       freelog();
       return -1;
    }

	if((funix = open(LogName, O_RDONLY))<0){
		freelog();
		return -1;
	}
    
	str.ic_cmd = I_CONSLOG;
	str.ic_timout = 0;
	str.ic_len = 0;
	str.ic_dp = NULL;
	if (ioctl(funix, I_STR, &str) < 0) {
		close (funix);
		freelog();
		return -1;
	}
	g_pollfd[g_in].fd = funix;
	g_pollfd[g_in].events = POLLIN;
	g_in++;

	return 1;
}


void  *monitor_log()
{
	int	i;
	int nfds;
	int flags = 0;
	char buf[MAXLINE+1];
	struct strbuf ctl;
	struct strbuf dat;
	struct log_ctl hdr;

	if(init()<0) return NULL;

	for (;1;) {

		monitor_wtmp( );
		errno = 0;
		if((nfds = poll(g_pollfd, g_in, 2000 )) <= 0){
			continue;
		}

		if (g_pollfd[0].revents & POLLIN) {
			dat.maxlen = MAXLINE;
			dat.buf = buf;
			ctl.maxlen = sizeof(struct log_ctl);
			ctl.buf = (caddr_t)&hdr;
			i = getmsg(g_pollfd[0].fd, &ctl, &dat, &flags);
			if (i >= 0 && dat.len > 0) {
				buf[dat.len] = '\0';
fprintf(stderr, "syslog_buf[%s]\n", buf);
				nfds--;
			} else if (i < 0 && errno != EINTR) {
				printf("klog.. \n");
				(void) close(g_pollfd[0].fd);
				g_pollfd[0].fd = -1;
				nfds--;
			}
		} else if (g_pollfd[0].revents & (POLLNVAL|POLLHUP|POLLERR)) {
			printf("klog.. \n");
			(void) close(g_pollfd[0].fd);
			g_pollfd[0].fd = -1;
		}
		i = 1;
	}
	return NULL;
}

void  monitor_wtmp( )
{
	struct utmpx ut;

	if ( read ( g_wtmpfd, &ut, sizeof(ut) ) <= 0 ) {
		return;
	}
fprintf(stderr, "ut_user[%s] | ut_id[%s] | ut_type[%d] | status[%d] | exit[%d] |\n", 	
		ut.ut_user, ut.ut_id, ut.ut_type, 
		ut.ut_exit.e_termination, ut.ut_exit.e_exit);
fprintf(stderr, "line[%s]\n##################################################\n", ut.ut_line);

}

void freelog ( 
{
   int   i;
   for ( i = 0 ; i < g_in ; i ++ )
      close ( g_pollfd[i].fd );
   close ( g_wtmpfd );
}

int main(int argc, char **argv)
{
	monitor_log();
	return 0;
}
