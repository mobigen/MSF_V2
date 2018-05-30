
#include <arpa/inet.h>
#include <netdb.h>
#include <stdlib.h>
#include <string.h>
#include <syslog.h>
#include <unistd.h>
#include <utmp.h>
#include <utmpx.h>

#include <sys/fcntl.h>
#include <sys/utsname.h>

#define SYNC_FILE	0x002	/* do fsync on file after printing */
#define ADDDATE		0x008	/* add a date to the message */
#define MARK		0x010	/* this message is a mark */
#define LOG_FAC(p)	(((p) & LOG_FACMASK) >> 3)
#define LOG_PRI(p)	((p) & LOG_PRIMASK)
#define	MAXLINE		2048	/* maximum line length */
#define DEFUPRI		(LOG_USER|LOG_INFO)
#define WTMPX_FILE	"/var/adm/wtmp"

#define ERROR       3
#define WARNING     2
#define INFORMATION 1

static char	*LogName = "/dev/log";
int g_wtmpfd;
int g_logfd;

void  *monitor_log();
void  wtmp_monitor();
void  freelog();
void  die(int);
int init();


int init()
{
    if((g_wtmpfd=open(WTMPX_FILE, O_RDONLY))<0){
       return -1;
    }

    if (lseek(g_wtmpfd, 0, SEEK_END) < 0){
       freelog ( );
       return -1;
    }

	if((g_logfd=open(LogName, O_RDONLY | O_NONBLOCK, 0))<0){
		freelog ( );
		return -1;
	}

	return 1;
}


void  *monitor_log()
{
	int	i;
	char line[MAXLINE+1];
	int nfds;
	int maxfds;
	fd_set readfds;
	struct timeval tv;

	if(init()<0) return NULL;

	FD_ZERO(&readfds);
	FD_SET(g_logfd, &readfds);
	maxfds = g_logfd;

	tv.tv_sec = 0;
	tv.tv_usec = 3000;

	for (;;) {

		wtmp_monitor();

		FD_ZERO(&readfds);
		FD_SET(g_logfd, &readfds);

		nfds = select(maxfds+1, (fd_set *) &readfds, (fd_set *) NULL,
				  (fd_set *) NULL, &tv);

		if (nfds <= 0) {
			continue;
		}

		if(read(g_logfd, line, MAXLINE)>0){
printf("line[%s]\n", line);
		}
	}
	return NULL;
}

void wtmp_monitor() {

	char OnOff_flag[2];
	struct utmp utmpEntry;

	/* 변경된 내용이 있는 경우 */
	if( read(g_wtmpfd, &utmpEntry, sizeof(struct utmp) )  > 0 ) {
		printf("utmpEntry.ut_type[%d]\n", utmpEntry.ut_type);
		printf("utmpEntry.ut_user[%s]\n", utmpEntry.ut_user);
		printf("utmpEntry.ut_id[%s]\n", utmpEntry.ut_id);
		printf("utmpEntry.ut_line[%s]\n", utmpEntry.ut_line);
	}
}

void die(int sig)
{
	close(g_logfd);
	close(g_wtmpfd);
	exit(0);
}


void freelog()
{
	close(g_wtmpfd);
	close(g_logfd);
}

int main(int argc, char **argv)
{
	monitor_log();
	return 0;
}
