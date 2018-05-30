
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_exit.c,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#include "u_exit.h"

/* static variable for status */
static exitstatus_t __exit[] = {
	{ STATUS_EX_OK         , "Termination (Success)"},
	{ STATUS_EX_ERROR      , "General error"},
	{ STATUS_EX_LICENSE    , "License expired"},
	{ STATUS_EX_RESETERR   , "Configuration error"},
	{ STATUS_EX_INITERR    , "Initialization error"},
	{ STATUS_EX_THRCREATE  , "Launch Thread error"},
	{ STATUS_EX_THRMUTEX   , "Mutex handle error"},
	{ STATUS_EX_THRCOND    , "Cond. var. handle error"},
	{ STATUS_EX_THRRWLK    , "Rwlock handle error"},
	{ STATUS_EX_SIGHUP     , "Hangup (SIGNAL)" },
	{ STATUS_EX_SIGINT     , "Interrupt (SIGNAL)" },
	{ STATUS_EX_SIGQUIT    , "Quit (SIGNAL)" },
	{ STATUS_EX_SIGILL     , "Illegal instruction (SIGNAL)" },
	{ STATUS_EX_SIGTRAP    , "Trace trap (SIGNAL)" },
	{ STATUS_EX_SIGABRT    , "Abort (SIGNAL)" },
	{ STATUS_EX_SIGIOT     , "IOT trap (SIGNAL)" },
	{ STATUS_EX_SIGBUS     , "BUS error (SIGNAL)" },
	{ STATUS_EX_SIGFPE     , "Floating-point exception (SIGNAL)" },
	{ STATUS_EX_SIGKILL    , "Kill, unblockable (SIGNAL)" },
	{ STATUS_EX_SIGUSR1    , "User-defined signal 1 (SIGNAL)" },
	{ STATUS_EX_SIGSEGV    , "Segmentation violation (SIGNAL)" },
	{ STATUS_EX_SIGUSR2    , "User-defined signal 2 (SIGNAL)" },
	{ STATUS_EX_SIGPIPE    , "Broken pipe (SIGNAL)" },
	{ STATUS_EX_SIGALRM    , "Alarm clock (SIGNAL)" },
	{ STATUS_EX_SIGTERM    , "Termination (SIGNAL)" },
	{ STATUS_EX_SIGSTKFLT  , "Stack fault" },
	{ STATUS_EX_SIGCHLD    , "Child status has changed (SIGNAL)" },
	{ STATUS_EX_SIGCONT    , "Continue (SIGNAL)" },
	{ STATUS_EX_SIGSTOP    , "Stop, unblockable (SIGNAL)" },
	{ STATUS_EX_SIGTSTP    , "Keyboard stop (SIGNAL)" },
	{ STATUS_EX_SIGTTIN    , "Background read from tty (SIGNAL)" },
	{ STATUS_EX_SIGTTOU    , "Background write to tty (SIGNAL)" },
	{ STATUS_EX_SIGURG     , "Urgent condition on socket (SIGNAL)" },
	{ STATUS_EX_SIGXCPU    , "CPU limit exceeded (SIGNAL)" },
	{ STATUS_EX_SIGXFSZ    , "File size limit exceeded (SIGNAL)" },
	{ STATUS_EX_SIGVTALRM  , "Virtual alarm clock (SIGNAL)" },
	{ STATUS_EX_SIGPROF    , "Profiling alarm clock (SIGNAL)" },
	{ STATUS_EX_SIGWINCH   , "Window size change (SIGNAL)" },
	{ STATUS_EX_SIGIO      , "I/O now possible (SIGNAL)" },
	{ STATUS_EX_SIGPWR     , "Power failure restart (SIGNAL)." },
	{ STATUS_EX_SIGSYS     , "Bad system call (SIGNAL)" },
	{ STATUS_EX_USAGE      , "Command line usage error" },
	{ STATUS_EX_DATAERR    , "Data format error" },
	{ STATUS_EX_NOINPUT    , "Cannot open input" },
	{ STATUS_EX_NOUSER     , "Addressee unknown" },
	{ STATUS_EX_NOHOST     , "Host name unknown" },
	{ STATUS_EX_UNAVAILABLE, "Service unavailable" },
	{ STATUS_EX_SOFTWARE   , "Internal software error" },
	{ STATUS_EX_OSERR      , "System error (e.g., can't fork)" },
	{ STATUS_EX_OSFILE     , "Critical OS file missing" },
	{ STATUS_EX_CANTCREAT  , "Can't create (user) output file" },
	{ STATUS_EX_IOERR      , "Input/output error" },
	{ STATUS_EX_TEMPFAIL   , "Temp failure; user is invited to retry" },
	{ STATUS_EX_PROTOCOL   , "Remote error in protocol" },
	{ STATUS_EX_NOPERM     , "Permission denied" },
	{ STATUS_EX_CONFIG     , "Configuration error" },
	{ STATUS_EX_EXEC       , "Exec's error" },
	{                    -1, "Unknwon"}
};

/*
 * func : xstatus_checkout
 * desc : 
 */

int xstatus_checkout(int xstatus)
{
	int x = 0;

	if (WIFSIGNALED(xstatus)) {
		x  = WTERMSIG(xstatus); 
		x += STATUS_EX_SIGNAL_START;
	}
	else 
		x  = WEXITSTATUS(xstatus);

	return x;
}

/*
 * func : xstatus_lookup
 * desc : 
 */

char *xstatus_lookup(int status)
{ 
	int i;

	i = 0;
	while (__exit[i]._stat != -1) {
		if (__exit[i]._stat == status) {
			return __exit[i].desc;
		}
		i++;
	}

	return __exit[i].desc;
}

/*
 * func : xstatus_copy
 * desc : 
 */

void xstatus_copy(int xstatus, char *desc)
{
	int  x;
	char *s;

	x = xstatus_checkout(xstatus);
	s = xstatus_lookup(x);

	/* ok. set the descript */
	sprintf(desc,"%s",s);
}

