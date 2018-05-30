
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_environ.h,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#ifndef _U_ENVIRON_H_
#define _U_ENVIRON_H_

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

/* user defined headers,, */
#include "u_time.h"
#include "u_debug.h"
#include "u_operate.h"
#include "u_dlist.h"


#ifdef __cplusplus
extern "C" 
{
#endif

/* user defined constant list,, */
#define MAX_LINE_SIZE  4096
#define NEWLINE_CHAR   0x0a /* \n */
#define COMMENT_CHAR   0x23 /*  # */
#define CONTINUE_CHAR  0x5c /* \\ */

/* prog's home directories */
#define PROGHOME "NEOSMSHOME"

/* user defined data structure list,, */
typedef struct _environ
{
	int  fd;
	char line[MAX_LINE_SIZE+1];
} environ_t;

typedef struct _environent
{
	char key[64];
	char value[MAX_LINE_SIZE+1];
} environent_t;

typedef h_node_t environlst_t;

/* function definitions,, */
/* environ related */
environ_t *openenv(char *filename, int oflag);
void closeenv(environ_t *environ);
char *readenv(environ_t *environ);

/* environlst related */
environlst_t *environlst_create(char *filename, int srchflag);
char *environlst_derive(environlst_t *envlst, const char *key);
void  environlst_destroy(environlst_t *envlst);
void  environlst_insert(environlst_t *envlst, environent_t *entries);
void  environlst_print(environlst_t *envlst);

/* ASMSHOME related */
char *guess_homeenv();
char *gethomeenv();
char *getpathenv();
char *lookuplocation(char *target, char *location);
void setpathenv(char *env);


#ifdef __cplusplus
}  /* end extern "C" */
#endif

#endif /* _U_ENVIRON_H_ */


