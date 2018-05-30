
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_signal.h,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#ifndef _U_SIGNAL_H_
#define _U_SIGNAL_H_

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* for strerrno() */
#include <unistd.h>
#include <errno.h>

/* for signal */
#include <signal.h>
#include <sys/time.h>

#include <strings.h> /* to use bzero func() */

/* the user defined header files.. */
#include "u_debug.h"


#ifdef __cplusplus
extern "C" 
{
#endif

#ifndef __SIGFUNC__
#define __SIGFUNC__
typedef void Sigfunc (int);     /* for signal handlers */
#endif

/* signal in blocking and non-reset mode.. */
Sigfunc *signal_rst(int signo, Sigfunc *func);
Sigfunc *signal_intr(int signo, Sigfunc *func);
Sigfunc *Signal(int signo, Sigfunc *func); /* will call sigintr */

/* block signal in a cerntain seconds.. */
int  sigwait_set();
void sigwait_unset();
int  sigwait_timeo(int timeo);
int  sigwait_pipe();

/* handler func */
void sigwait_handler(int signo);

void sigwait_block();
void sigwait_unblock();

/* SIGSEGV, SIGBUS */
void bug_catcher_install(char *log);
void bug_catcher(int signo);


#ifdef __cplusplus
}  /* end extern "C" */
#endif

#endif /* _U_SIGNAL_H_ */

