
#include <arpa/inet.h>
#include <ctype.h>
#include <netinet/in.h>
#include <netdb.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <utmp.h>

#include <sys/errno.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/syslog.h>
#include <sys/un.h>
#include <sys/utsname.h>

#define	MAXLINE	1024	/* maximum line length */
#define DEFUPRI	(LOG_USER|LOG_NOTICE)

#ifndef _PATH_LOG
#define _PATH_LOG	"/dev/log"
#endif

#define _PATH_WTMP	"/var/log/wtmp"
#define MAXFUNIX	20

#define SYNC_FILE	0x002	/* do fsync on file after printing */
#define ADDDATE		0x004	/* add a date to the message */
#define MARK		0x008	/* this message is a mark */

#define MAX_HOST_LEN	256
#define MAX_IP_LEN	15

extern int errno;
static int restart = 0;

int	Initialized = 0;	/* set when we have initialized ourselves */

/* wtmp_monitor */
int i_wtmp;
FILE *fp_wtmp;
char str_ut_type[11][32] = {
	"EMPTY", "RUN_LVL", "BOOT_TIME", "NEW_TIME", "OLD_TIME",
	"INIT_PROCESS", "LOGIN_PROCESS", "USER_PROCESS", "DEAD_PROCESS",
	"ACCOUNTING", };

struct utmp *utmpEntry;
int g_sd;
time_t	now;

/* Function prototypes. */
void printchopped(const char *hname, char *msg, int len, int fd);
void printline(const char *hname, char *msg);
void logmsg(int pri, char *msg, const char *from, int flags);
void wtmp_monitor();
int init();
static int create_unix_socket(const char *path);

void* monitor_log()
{
	register int i;
	register char *p;

	int len, maxfds;
	int	fd;
	struct sockaddr_un fromunix;
	struct hostent *hent;
	char line[MAXLINE +1];
	fd_set allset, rfds;
	struct timeval tv;

	tv.tv_sec = 0;
	tv.tv_usec = 3000;

	FD_ZERO(&allset);

	if( init() < 0)	return NULL;

	for (;;) {
		int nfds;
		errno = 0;
		maxfds = 0;

		wtmp_monitor();

		usleep(1000);

		FD_ZERO(&rfds);
		FD_SET(g_sd, &rfds);

		for(nfds=0;nfds<FD_SETSIZE;++nfds){
			if(FD_ISSET(nfds, &allset)){
				FD_SET(nfds, &rfds);
			}
		}

		g_sd > nfds ? (maxfds=g_sd):(maxfds=nfds);

		nfds = select(maxfds+1, (fd_set *) &rfds, (fd_set *) NULL,
				  (fd_set *) NULL, &tv);

		if (nfds <= 0) {
			continue;
		}
		for(fd=0;fd<=maxfds;++fd){
			if ( FD_ISSET(fd, &rfds) && FD_ISSET(fd, &allset)) {
				memset(line, 0x00, sizeof(line));
				errno=0;
				i = read(fd, line, sizeof(line)-1);
				if (i > 0) {
printf("fd[%d] line[%s]\n", fd, line);
			  	} else if (i < 0) {
			    	if (errno != EINTR) {
			      		printf("recvfrom unix error[%d][%s]\n", g_sd, strerror(errno));
					}
				} else {
					printf("Unix socket (%d) closed.\n", fd);
					/* reset it */
					close(fd);
					FD_CLR(fd, &allset);
			   }
	      	}
		}

		if(FD_ISSET(g_sd, &rfds)){
			len = sizeof(fromunix);
			if((fd = accept(g_sd, (struct sockaddr *)&fromunix, (socklen_t *)&len))>=0){
				FD_SET(fd, &allset);
			}
		}
	}
	return NULL;
}


void wtmp_monitor() {

	/* 변경된 내용이 있는 경우 */
	if( fread(utmpEntry, sizeof(struct utmp), 1, fp_wtmp) > 0 ) {
		fprintf(stderr, "utmp entry : type[%d], line[%s], user[%s]\n",
			utmpEntry->ut_type, utmpEntry->ut_line, utmpEntry->ut_user);
	}
}


int init()
{
	register int i;
	struct utsname name_info;
	struct stat wtmp_stat;

	if ((g_sd = create_unix_socket("/dev/log")) != -1)
		printf("Opened UNIX socket `%d'.\n", g_sd);

	/* wtmp_monitor initialize */
	i_wtmp = 0;
	if( (utmpEntry = (struct utmp *)malloc(sizeof(struct utmp)) ) == NULL ) {
		return -1;
	}

	if( stat(_PATH_WTMP, &wtmp_stat) != 0 ) {
		fprintf(stderr, "[%s,%d] stat error[%s]\n", __FILE__, __LINE__, strerror(errno));
		return -1;
	}

	if( (fp_wtmp = fopen( _PATH_WTMP, "r")) == NULL ) {
		fprintf(stderr, "[%s,%d] file open error[%s]\n", __FILE__, __LINE__, strerror(errno));
		return -1;
	}

	fseek(fp_wtmp, 0L, SEEK_END);
	return 1;
}


static int create_unix_socket(const char *path)
{
	struct sockaddr_un sunx;
	int fd;

	if (path[0] == '\0')
		return -1;

	(void) unlink(path);

	memset(&sunx, 0, sizeof(sunx));
	sunx.sun_family = AF_UNIX;
	(void) strncpy(sunx.sun_path, path, sizeof(sunx.sun_path));
	fd = socket(AF_UNIX, SOCK_STREAM, 0);
	if (fd < 0 || bind(fd, (struct sockaddr *) &sunx,
			   sizeof(sunx.sun_family)+strlen(sunx.sun_path)) < 0 ||
	    chmod(path, 0666) < 0 || listen(fd, 5) < 0) {
		printf("cannot create %s (%s).\n", path, strerror(errno));
		close(fd);
	}
	return fd;
}

int main(int argc, char **argv)
{
	monitor_log();
	return 0;
}
