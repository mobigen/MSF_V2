/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_exit.h,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#ifndef _U_EXIT_H_
#define _U_EXIT_H_

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>

#include <signal.h>
#include <sys/types.h>
#include <sys/wait.h>


#ifdef __cplusplus
extern "C" 
{
#endif

#ifdef CYGWIN
#ifndef SIGIOT
#define SIGIOT SIGABRT 
#endif // SIGIOT

#ifndef SIGPWR
#define SIGPWR SIGSYS
#endif // 
#endif 

/* user defined constant list */
#define STATUS_EX_OK            0
#define STATUS_EX_ERROR         1 
#define STATUS_EX_LICENSE       2 
#define STATUS_EX_RESETERR      3 
#define STATUS_EX_INITERR       4 
#define STATUS_EX_THRCREATE     31 
#define STATUS_EX_THRMUTEX      32 
#define STATUS_EX_THRCOND       33 
#define STATUS_EX_THRRWLK       34 

#define STATUS_EX_USAGE         64 
#define STATUS_EX_DATAERR       65 
#define STATUS_EX_NOINPUT       66 
#define STATUS_EX_NOUSER        67 
#define STATUS_EX_NOHOST        68 
#define STATUS_EX_UNAVAILABLE   69 
#define STATUS_EX_SOFTWARE      70 
#define STATUS_EX_OSERR         71 
#define STATUS_EX_OSFILE        72 
#define STATUS_EX_CANTCREAT     73 
#define STATUS_EX_IOERR         74 
#define STATUS_EX_TEMPFAIL      75 
#define STATUS_EX_PROTOCOL      76 
#define STATUS_EX_NOPERM        77 
#define STATUS_EX_CONFIG        78

#define STATUS_EX_UNKNOWN       126
#define STATUS_EX_EXEC          127

#define STATUS_EX_SIGNAL_START  128 
#define STATUS_EX_SIGHUP        STATUS_EX_SIGNAL_START + SIGHUP
#define STATUS_EX_SIGINT        STATUS_EX_SIGNAL_START + SIGINT
#define STATUS_EX_SIGQUIT       STATUS_EX_SIGNAL_START + SIGQUIT
#define STATUS_EX_SIGILL        STATUS_EX_SIGNAL_START + SIGILL
#define STATUS_EX_SIGTRAP       STATUS_EX_SIGNAL_START + SIGTRAP
#define STATUS_EX_SIGABRT       STATUS_EX_SIGNAL_START + SIGABRT
#define STATUS_EX_SIGIOT        STATUS_EX_SIGNAL_START + SIGIOT
#define STATUS_EX_SIGBUS        STATUS_EX_SIGNAL_START + SIGBUS
#define STATUS_EX_SIGFPE        STATUS_EX_SIGNAL_START + SIGFPE
#define STATUS_EX_SIGKILL       STATUS_EX_SIGNAL_START + SIGKILL
#define STATUS_EX_SIGUSR1       STATUS_EX_SIGNAL_START + SIGUSR1
#define STATUS_EX_SIGSEGV       STATUS_EX_SIGNAL_START + SIGSEGV
#define STATUS_EX_SIGUSR2       STATUS_EX_SIGNAL_START + SIGUSR2
#define STATUS_EX_SIGPIPE       STATUS_EX_SIGNAL_START + SIGPIPE
#define STATUS_EX_SIGALRM       STATUS_EX_SIGNAL_START + SIGALRM
#define STATUS_EX_SIGTERM       STATUS_EX_SIGNAL_START + SIGTERM
#ifdef SIGSTKFLT
# define STATUS_EX_SIGSTKFLT     STATUS_EX_SIGNAL_START + SIGSTKFLT
#else
# define STATUS_EX_SIGSTKFLT     STATUS_EX_UNKNOWN
#endif
#define STATUS_EX_SIGCHLD       STATUS_EX_SIGNAL_START + SIGCHLD
#define STATUS_EX_SIGCONT       STATUS_EX_SIGNAL_START + SIGCONT
#define STATUS_EX_SIGSTOP       STATUS_EX_SIGNAL_START + SIGSTOP
#define STATUS_EX_SIGTSTP       STATUS_EX_SIGNAL_START + SIGTSTP
#define STATUS_EX_SIGTTIN       STATUS_EX_SIGNAL_START + SIGTTIN
#define STATUS_EX_SIGTTOU       STATUS_EX_SIGNAL_START + SIGTTOU
#define STATUS_EX_SIGURG        STATUS_EX_SIGNAL_START + SIGURG
#define STATUS_EX_SIGXCPU       STATUS_EX_SIGNAL_START + SIGXCPU
#define STATUS_EX_SIGXFSZ       STATUS_EX_SIGNAL_START + SIGXFSZ
#define STATUS_EX_SIGVTALRM     STATUS_EX_SIGNAL_START + SIGVTALRM
#define STATUS_EX_SIGPROF       STATUS_EX_SIGNAL_START + SIGPROF
#define STATUS_EX_SIGWINCH      STATUS_EX_SIGNAL_START + SIGWINCH
#define STATUS_EX_SIGIO         STATUS_EX_SIGNAL_START + SIGIO
#define STATUS_EX_SIGPWR        STATUS_EX_SIGNAL_START + SIGPWR
#define STATUS_EX_SIGSYS        STATUS_EX_SIGNAL_START + SIGSYS

/* user defined data struct list */
typedef struct _exitstatus
{
	int  _stat;
	char *desc;
} exitstatus_t;

/* user defined function list */
int   xstatus_checkout(int xstatus);
char *xstatus_lookup(int status);
void xstatus_copy(int xstatus, char *desc);


#ifdef __cplusplus
}  /* end extern "C" */
#endif

#endif /* _U_EXIT_H_ */


