
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_process.h,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#ifndef _U_PROCESS_H_
#define _U_PROCESS_H_

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <ctype.h>

/* the user defined header files,, */
#include "u_debug.h"
#include "u_exit.h"
#include "u_environ.h"
#include "u_signal.h"


#ifdef __cplusplus
extern "C" 
{
#endif

#define LP_MAXFD 64

/* data struct definition */
typedef struct _ldshell
{
	int  fd;
	int  child;
	char line[4096];
} ldshell_t;

/* function definition */
int    ld_count(char *s);
char **ld_alloc(char *s);
void   ld_release(char ***params);

/* - function to load process,, - */
int load_process(char *loc, char *cmdline);
int daemon_init();

/* ldshell API */
ldshell_t *lsh_open(char *cmdline);
int  lsh_close(ldshell_t *lsh);
int  lsh_shutdown(ldshell_t *lsh, int signo);
void lsh_execute(char *cmdline, int fd[]);
void lsh_ext_execute(char *cmdline, int fds[]);
int  lsh_setup();
void lsh_cleanup(int signo);

int  lsh_readline(ldshell_t *lsh, char *line, int maxlen, int timeo);


#ifdef __cplusplus
}  /* end extern "C" */
#endif

#endif /* _U_PROCESS_H_ */


