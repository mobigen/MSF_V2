
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_signal.c,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#include "u_signal.h"

/*
 * func : signal_rst
 * desc : 
 */

Sigfunc *signal_rst(int signo, Sigfunc *func)
{
	struct sigaction act, oact;

	/* func name,, */
	printout(__F__,"signal_rst");

#if 0
	/* not sure in all the specfic machine.. */
	return ( signal(signo, func) );
#else
	act.sa_handler = func;
	sigemptyset(&act.sa_mask);
	act.sa_flags   = 0;

	if ( signo == SIGALRM ) {
#ifdef SA_INTERRUPT
		act.sa_flags |= SA_INTERRUPT;
#endif
	} else {
#ifdef SA_RESTART
		act.sa_flags |= SA_RESTART;
#endif
	}

	if ( sigaction(signo, &act, &oact) < 0 ) 
		return (SIG_ERR);

	return (oact.sa_handler);
#endif

}

/*
 * func : signal_intr
 * desc : 
 */

Sigfunc *signal_intr(int signo, Sigfunc *func)
{
	struct sigaction	act, oact;

	/* func name,, */
	/* printout(__F__,"signal_intr"); */

	act.sa_handler = func;
	sigemptyset(&act.sa_mask);
	act.sa_flags = 0;

#ifdef	SA_INTERRUPT	/* SunOS */
	act.sa_flags |= SA_INTERRUPT;
#endif
	if (sigaction(signo, &act, &oact) < 0)
		return(SIG_ERR);

	return(oact.sa_handler);
}

/*
 * func : Signal
 * desc : 
 */

Sigfunc *Signal(int signo, Sigfunc *func)
{

	/* func name,, */
	/* printout(__F__,"Signal"); */

	return (signal_intr(signo, func));
}

/*
 * func : sigwait_set
 * desc : 
 */

int pipefd[2] = { -1, -1 };

int sigwait_set()
{
	int icheck;

	/* func name,, */
	printout(__F__,"sigwait_set"); 

	icheck = 0;
	if (pipe(pipefd) != -1) {
		Signal(SIGHUP , sigwait_handler);
		Signal(SIGTERM, sigwait_handler);
		Signal(SIGINT , sigwait_handler);
		Signal(SIGUSR1, sigwait_handler);
		Signal(SIGUSR2, sigwait_handler);
		Signal(SIGALRM, sigwait_handler);
		Signal(SIGCHLD, sigwait_handler);

		icheck   = 1;
	} else 
		printout(__M__,"sigwait_set: fail to pipe.");

	return icheck;
}

/*
 * func : sigwait_unset
 * desc : 
 */

void sigwait_unset()
{
	/* func name,, */
	printout(__F__,"sigwait_unset"); 

	if (pipefd[0] != -1)
		close(pipefd[0]);

	if (pipefd[1] != -1)
		close(pipefd[1]);
}

/*
 * func : sigwait_timeo
 * desc : 
 */

int sigwait_timeo(int timeo)
{
	fd_set  rset;
	int     nfds, signo;
	struct  timeval  tval;

	/* func name,, */
	printout(__F__,"sigwait_timeo"); 

	/* time out,, */
	tval.tv_sec  = timeo;
	tval.tv_usec = 0;

	/* readability,, */
	FD_ZERO(&rset);
	FD_SET(pipefd[0], &rset);

	errno = 0;
	if ((nfds = select(pipefd[0] + 1, &rset, 
			NULL, NULL, (timeo == 0) ? NULL: &tval)) == 0) 
	{
		errno = ETIMEDOUT;
		signo = 0;
	} else {
		if (FD_ISSET(pipefd[0], &rset)) {
			if (read(pipefd[0], &signo, sizeof(signo)) != sizeof(signo)) {
				printout(__M__,"sigwait_timeo: fail to read.");
				signo = -1;
			} 
		} else {
			if (nfds == -1 && errno != EINTR) {
				printout(__M__,"sigwait_timeo: fail to select.");
				signo = -1;
			} else {
				printout(__M__,"sigwait_timeo: fail to select.");
				signo = 0;
			}
		}
	}
	
	return signo;
}

/*
 * func : sigwait_pipe
 * desc : 
 */

int sigwait_pipe()
{
	/* func name,, */
	printout(__F__,"sigwait_pipe"); 

	return pipefd[0];
}

/*
 * func : sigwait_handler
 * desc : 
 */

void sigwait_handler(int signo)
{
	/* func name,, */
	printout(__F__,"sigwait_handler"); 

	if (write(pipefd[1], &signo, sizeof(signo)) != sizeof(signo)) 
		printout(__M__,
			"sigwait_handler: fail to write to pipe(%d).", pipefd[1]);

	return;
}

/*
 * func : sigwait_block
 * desc : 
 */

void sigwait_block()
{
	sigset_t signal_to_block;

	/* func name,, */
	printout(__F__,"sigwait_block"); 

	sigemptyset(&signal_to_block);
	sigaddset(&signal_to_block, SIGHUP);
	sigaddset(&signal_to_block, SIGTERM);
	sigaddset(&signal_to_block, SIGINT);
	sigaddset(&signal_to_block, SIGUSR1);
	sigaddset(&signal_to_block, SIGUSR2);
	sigaddset(&signal_to_block, SIGALRM);
	sigaddset(&signal_to_block, SIGCHLD);

	sigprocmask(SIG_BLOCK, &signal_to_block, NULL);

	return;
}

/*
 * func : sigwait_unblock
 * desc : 
 */

void sigwait_unblock()
{
	sigset_t signal_to_unblock;

	/* func name,, */
	printout(__F__,"sigwait_unblock"); 

	sigemptyset(&signal_to_unblock);
	sigaddset(&signal_to_unblock, SIGHUP);
	sigaddset(&signal_to_unblock, SIGTERM);
	sigaddset(&signal_to_unblock, SIGINT);
	sigaddset(&signal_to_unblock, SIGUSR1);
	sigaddset(&signal_to_unblock, SIGUSR2);
	sigaddset(&signal_to_unblock, SIGALRM);
	sigaddset(&signal_to_unblock, SIGCHLD);

	sigprocmask(SIG_UNBLOCK, &signal_to_unblock, NULL);

	return;
}

/*
 * func : bug_catcher
 * desc : 
 */

void bug_catcher(int signo)
{
	/* func name,, */
	printout(__F__,"bug_catcher"); 

	/* oops.. */
	printout(__M__, "bug_catcher: the signal (%s) is catched.", 
			(signo == SIGBUS) ? "SIGBUS" : "SIGSEGV");

	/* reset the signal to default */
	signal(signo, SIG_DFL);

	/* kill myself */
	kill(signo, getpid());
}

/*
 * func : bug_catcher_install
 * desc : 
 */

void bug_catcher_install(char *logs)
{
	printout(__F__,"bug_catcher_install"); 

	/* then set signal,,, */
	signal(SIGBUS, bug_catcher);
	signal(SIGSEGV, bug_catcher);
}


