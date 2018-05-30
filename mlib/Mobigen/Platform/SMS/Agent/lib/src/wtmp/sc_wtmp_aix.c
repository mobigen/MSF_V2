#include <sys/types.h>
#include <strings.h>
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


/* #define	MAXLINE	1024 */	/* maximum line length */
#define	MAXLINE	900		/* maximum line length */
#define DEFUPRI	(LOG_USER|LOG_NOTICE)

#ifndef _PATH_LOG
#define _PATH_LOG	"/dev/log"
#endif

#define _PATH_WTMP	"/var/adm/wtmp"
#define MAXFUNIX	20

#define SYNC_FILE	0x002	/* do fsync on file after printing */
#define ADDDATE		0x004	/* add a date to the message */
#define MARK		0x008	/* this message is a mark */

#define MAX_HOST_LEN	256
#define MAX_IP_LEN	15

#define LOG_FAC(p)      (((p) & LOG_FACMASK) >> 3)
#define LOG_PRI(p)      ((p) & LOG_PRIMASK)

/* Global Variable Declaration */
extern int errno;
static int restart = 0;
int nfunix = 1;
int	Initialized = 0;	/* set when we have initialized ourselves */
int funix[MAXFUNIX] = { -1, };
char **parts;
char *funixn[MAXFUNIX] = { _PATH_LOG };
char LocalHostName[256];	/* our hostname */
char *LocalDomain;		/* our local domain name */
char g_HostName[MAX_HOST_LEN+1];
char g_HostIP[MAX_IP_LEN+1];

/* wtmp_monitor */
int i_wtmp;
FILE *fp_wtmp;
char str_ut_type[11][32] = {
	"EMPTY", "RUN_LVL", "BOOT_TIME", "NEW_TIME", "OLD_TIME",
	"INIT_PROCESS", "LOGIN_PROCESS", "USER_PROCESS", "DEAD_PROCESS",
	"ACCOUNTING", };

struct utmp *utmpEntry;
struct stat wtmp_stat;
ino_t orig_inode_wtmp;
off_t orig_size_wtmp;
time_t	now;

void wtmp_monitor();
int init();
static int create_unix_socket(const char *path);

void* monitor_log()
{
	register int i;
	register char *p;

	int len, num_fds;
	int	fd;
	int maxfds;
	struct sockaddr_un fromunix;
	struct hostent *hent;
	char line[MAXLINE +1];
	fd_set unixm, readfds;
	int nfds;
	struct timeval tv;

	/* select 기다리는 시간 설정 */
	tv.tv_sec = 0;
	tv.tv_usec = 3000;

	chdir ("/");

	for (i = 1; i < MAXFUNIX; i++) {
		funixn[i] = "";
		funix[i]  = -1;
	}

	if( init() < 0 ) return NULL;

	/* Main loop begins here. */
	FD_ZERO(&unixm);
	for (;;) {

		FD_ZERO(&readfds);
		wtmp_monitor();
		usleep(2000);

		/* Copy master connections */
		for (i = 0; i < nfunix; i++) {
			if (funix[i] != -1) {
				FD_SET(funix[i], &readfds);
				if (funix[i]>maxfds) maxfds=funix[i];
			}
		}
		/* Copy accepted connections */
		for (nfds= 0; nfds < FD_SETSIZE; ++nfds)
			if (FD_ISSET(nfds, &unixm)) {
				FD_SET(nfds, &readfds);
				if (nfds>maxfds) maxfds=nfds;
			}

		nfds = select(maxfds+1, (fd_set *) &readfds, (fd_set *) NULL,
				  (fd_set *) NULL, &tv);

		if (nfds == 0) {
			continue;
		}
		if (nfds < 0) {
			continue;
		}

		for (fd= 0; fd <= maxfds; ++fd)
		  if ( FD_ISSET(fd, &readfds) ) {
			memset(line, '\0', sizeof(line));
			i = recvfrom(fd, line, MAXLINE, 0, NULL, NULL);
			if (i > 0) {
printf("line[%s][%d]\n", line, fd);
		  	} else if (i < 0) {
		    	if (errno != EINTR) {
		      		printf("recvfrom unix error \n");
				}
			}
      	}
	}
	return NULL;
}


void wtmp_monitor() {

	char OnOff_flag[2];
	struct utmp tmp;

	memset(&tmp, 0x00, sizeof(struct utmp));
	if(fread(&tmp, sizeof(struct utmp), 1, fp_wtmp) > 0 ) {
		printf("type[%d], user[%s], line[%s]\n", tmp.ut_type,
			tmp.ut_user, tmp.ut_line);
	}
}


int init()
{
	register int i;
	struct utsname name_info;

	for (i = 0; i < nfunix; i++) {
		if (funix[i] != -1)
			close(funix[i]);
		if ((funix[i] = create_unix_socket(funixn[i])) != -1)
			printf("create unix socket[%s].\n", funixn[i]);
	}

	/* wtmp_monitor initialize */
	i_wtmp = 0;

	if( stat(_PATH_WTMP, &wtmp_stat) != 0 ) {
		fprintf(stderr, "stat error[%s]\n", strerror(errno));
		return -1;
	}
	orig_inode_wtmp = wtmp_stat.st_ino;
	orig_size_wtmp = wtmp_stat.st_size;

	if( (fp_wtmp = fopen( _PATH_WTMP, "r")) == NULL ) {
		fprintf(stderr, "file open error[%s]\n", strerror(errno));
		return -1;
	}

	fseek(fp_wtmp, 0L, SEEK_END);
	Initialized = 1;

	return 0;
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

	fd = socket(AF_UNIX, SOCK_DGRAM, 0);

	if (fd < 0 || bind(fd, (struct sockaddr *) &sunx, SUN_LEN(&sunx)) || chmod(path, 0666) < 0 ) {
		printf("cannot create %s (%d).\n", path, errno);
		close(fd);
	}

	return fd;
}


int main(int argc, char **argv)
{
	monitor_log();
	return 0;
}
