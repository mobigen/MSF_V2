
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_process.c,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#include "u_process.h"

static char *Shell;
static int IsAlarmed = 0;

void lsh_handle_alarm(int signo);

/*
 * func : daemon_init
 * desc : daemon process 로 변환
 */
int daemon_init()
{
	pid_t pid;
	int   fd;

	/* func name,, */
	printout(__F__,"daemon_init");

	if((pid = fork()) < 0)
		return -1;
	else if(pid != 0)
		exit(0);

	setsid();
	umask(0);
#if 0
	chdir("/");
#endif

	fd = open("/dev/null", O_RDWR);
	dup2(fd, 0);
	dup2(fd, 1);
	dup2(fd, 2);
	close(fd);

	return 0;
}

/*
 * func : lp_count
 * desc : argv 갯수를 헤아림
 */
int lp_count(char *s)
{
	int  len, icount, i;
	char *cp, *ep, c1, c2;

	/* func name,, */
	printout(__F__,"lp_count");

	len = strlen(s);
	if (*s == '\0' || len == 0)
		return 0;

	ep = s+len;
	while (isspace((int)(*ep)) || *ep == '\0') {
		ep--;
		len--;
	}

	icount = 1, cp = s;
	c2 = *cp;

	for (i = 0; i < len; i++) {
		c1 = *(cp+i);
		if (isspace((int)c1) && !isspace((int)c2))
			icount++;
		c2 = c1;
	}

	return icount;
}

/*
 * func : lp_alloc
 * desc : argv 할당
 */
char **lp_alloc(char *s)
{
	int  len, argc, i;
	char **param, *sp, *cp, *ep;

	/* func name,, */
	printout(__F__,"lp_alloc");

	if ((argc = lp_count(s)) != 0) {
		if ((param = (char **)malloc((argc+1)*sizeof(char *))) != NULL) {
			sp = s;
			for (i = 0; i < argc; i++) {
				while ( isspace((int)(*sp)) ) sp++;
				ep = cp = sp;

				while ( !isspace((int)(*ep)) && *ep != '\0' ) ep++;
				len = ep - cp;

				param[i] = (char *)malloc(len+1);
				memset(param[i], 0x00, len+1);
				memcpy(param[i], cp  , len);
				sp = ep;
			}

			param[argc] = NULL;
		}
	} else
		param = NULL;

	return param;
}

/*
 * func : lp_release
 * desc : argv 해제
 */

void lp_release(char ***params)
{
	char **p;
	int i;

	/* func name,, */
	printout(__F__,"lp_release");

	if ((p = *params) != NULL) {
		for (i = 0; p[i]; i++) free(p[i]);
		free(p);
		p = NULL;
	}

	return;
}

/*
 * func : load_process
 * desc : command를 load
 */
int load_process(char *where, char *cmdline)
{
	int pid;

	/* func name,, */
	printout(__F__,"load_process");

	if ((pid = fork()) == -1) 
		printout(__M__,"load_process: fail to fork.");
	else if (pid == 0) { /* child */
		char **param;
		int  fd;
		
		/* close all the file descript that parent opened */
		for (fd = 3; fd < LP_MAXFD; fd++)
			close(fd);

		/* ok.. allocate params and execute */
		errno = 0;
		if ((param = lp_alloc(cmdline)) != NULL) {
			execv(where, param);
			lp_release(&param);
		}

		/* oops.. error!! */
		printout(__M__,"load_process: fail to exec \"%s\".", cmdline);

		exit(STATUS_EX_EXEC);
	} 

	return pid;
}

/*
 * func : lsh_open
 * desc : 
 */
ldshell_t *lsh_open(char *cmdline)
{
	ldshell_t *lsh;
	int fdesc[2], child;

	/* func */
	printout(__F__,"lsh_open");

	/* setup the shell */
	if (!Shell && lsh_setup() == -1) {
		printout(__M__,"lsh_open: fail to lsh_setup.");
		return NULL;
	}
	
	/* create pipe.. */
	if (pipe(fdesc) == -1) {
		printout(__M__,"lsh_open: fail to pipe.");
		return NULL;
	}

	/* fork.. */
	if ((child = fork()) == -1) {
		printout(__M__,"lsh_open: fail to fork.");

		/* close all the pipe */
		close(fdesc[0]);
		close(fdesc[1]);
		
		return NULL;
	}
	else if (child == 0) /* child 1 */
#if 1
		lsh_ext_execute(cmdline, fdesc);
#else
		lsh_execute(cmdline, fdesc);
#endif

	/* close the write side.. */
	close(fdesc[1]);

	/* if it fails  */
	lsh = (ldshell_t*)malloc(sizeof(ldshell_t));
	lsh->fd    = fdesc[0];
	lsh->child = child;

	return lsh;
}

/*
 * func : lsh_close
 * desc : 
 */
int lsh_close(ldshell_t *lsh)
{
	/* func */
	printout(__F__,"lsh_close");

	/* release all the stuff */
	close(lsh->fd);

	free(lsh);

	return 1;
}

/*
 * func : lsh_shutdown
 * desc : 
 */
int lsh_shutdown(ldshell_t *lsh, int signo)
{
	/* func */
	printout(__F__,"lsh_shutdown");

	/* kill running child */
	kill(lsh->child, (signo == SIGTERM) ? SIGTERM : SIGKILL);

	return lsh_close(lsh);
}

/*
 * func : lsh_execute
 * desc : 
 */
void lsh_execute(char *cmdline, int fds[])
{
	int i;

	/* func */
	printout(__F__,"lsh_execute");

	/* close all the open files */
	for (i = 3; i < LP_MAXFD; i++)
		if (fds[1] != i)
			close(i);

	/* redirect the output */
	dup2(fds[1], fileno(stdin));
	dup2(fds[1], fileno(stdout));
	dup2(fds[1], fileno(stderr));

	/* then close.. */
	close(fds[1]);

	/* execute */
	execl(Shell,"sh","-c",cmdline,(char *)0);

	/* shell not found.. */
	printout(__M__,"lsh_execute: fail to exec (%s -> %s).", Shell, cmdline);

	exit(STATUS_EX_EXEC);
}

/*
 * func : lsh_execute
 * desc : 
 */
void lsh_ext_execute(char *cmdline, int fds[])
{
	int i, child;

	/* func */
	printout(__F__,"lsh_ext_excute.");

	/* install signal */
	signal(SIGHUP , SIG_DFL);
	signal(SIGUSR1, SIG_DFL);
	signal(SIGUSR2, SIG_DFL);
	signal(SIGALRM, SIG_DFL);
	signal(SIGINT , lsh_cleanup);
	signal(SIGTERM, lsh_cleanup);
	signal(SIGCHLD, lsh_cleanup);

	/* close the open files */
	for (i = 3; i < LP_MAXFD; i++) {
		if (fds[0] == i || fds[1] == i) continue;
		close(i);
	}

	/* be group reader */
	if (setpgid(0,0) == -1) {
		printout(__M__,"lsh_ext_execute: fail to setpgid.");
		exit(STATUS_EX_OSERR);
	}

	/* fork again */
	if ((child = fork()) == -1) {
		printout(__M__,"lsh_ext_execute: fail to fork.");

		/* close all the pipe */
		close(fds[0]);
		close(fds[1]);
		
		/* don't care.. */
		exit(STATUS_EX_OSERR);
	}
	else if (child == 0) { /* child 2 */
		/* close the read side */
		close(fds[0]);

		/* duplicate */
		dup2(fds[1], fileno(stdin));
		dup2(fds[1], fileno(stdout)); 
		dup2(fds[1], fileno(stderr));

		/* then, close */
		close(fds[1]);

		/* execute */
		execl(Shell,"sh","-c",cmdline,(char *)0);

		/* shell not found.. */
		printout(__M__,"lsh_ext_execute: fail to exec (%s -> %s).", Shell, cmdline);

		exit(STATUS_EX_EXEC);
	}
	
	/* I don't use them anymore */
	close(fds[0]);
	close(fds[1]);
	
	/* wait until got signal.. */
	while (1) pause();
}

/*
 * func : lsh_readline
 * desc : 
 */
int lsh_readline(ldshell_t *lsh, char *line, int maxlen, int timeo)
{
	int   n, cc;
	char *lptr, c;

	/* old handler */
	Sigfunc *ofunc;

	/* func */
	printout(__F__,"lsh_readline");

	/* setup the alarm */
	ofunc = Signal(SIGALRM, lsh_handle_alarm);
	if ((n = alarm(timeo)) != 0)
		printout(__M__,"lsh_readline: the alarm has already been set.");
	
	lptr = line;
	for (n = 1; n < maxlen; n++) {
again:
		if ((cc = read(lsh->fd,&c,1)) == 1) {
			*lptr++ = c;

			if (c == '\n')
				break;
		}
		else if (cc == 0) {
			if (n == 1)
				return 0; 
			else
				break;
		}
		else if (errno == EINTR && IsAlarmed) {
			/* restore the alarm */
			alarm(0);
			Signal(SIGALRM, ofunc);

			/* reset the alarm flag */
			IsAlarmed = 0;

			return -1;
		}
		else 
			goto again;
	}
	*lptr = '\0';

	/* replace '%s' to '%%' */
	replace_char(line,'%','*');

	/*
	 * turn off the current alarm,
	 * and restore to the previous one
	 */
	alarm(0);
	Signal(SIGALRM, ofunc);

	return n;
}

/*
 * func : lsh_handle_alarm
 * desc : 
 */
void lsh_handle_alarm(int signo)
{
	/* func */
	printout(__F__,"lsh_handle_alarm");

	IsAlarmed = 1;
}

/*
 * func : lsh_setup
 * desc : 
 */
int lsh_setup()
{
	char tmp[256];

	/* lookup shell */
	if (lookuplocation("sh",tmp) == NULL) {
		printout(__M__,"lsh_setup: fail to lookuplocation (sh).");
		return -1;
	}
	else
		Shell = strdup(tmp);

	return 1;
}

/*
 * func : lsh_cleaner
 * desc : 
 */

void lsh_cleanup(int signo)
{
	int status;

	/* func */
	printout(__F__,"lsh_cleaner");

	/* in case child shutdown */
	if (signo == SIGCHLD) {
		wait(&status);
		status = xstatus_checkout(status);

		/* normal exit */
		exit(status);
	}

	/* in case kill is signaled */
	signal(SIGTERM,SIG_DFL);

	/* kill all */
	kill(0,SIGTERM);
}

