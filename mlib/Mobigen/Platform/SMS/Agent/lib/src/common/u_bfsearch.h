
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_bfsearch.h,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#ifndef  _U_BFSEARCH_H_
#define  _U_BFSEARCH_H_

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>     /* errno */
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

/* user defined header */
#include "u_debug.h"
#include "u_missing.h"
#include "u_tokenize.h"


#ifdef __cplusplus
extern "C" 
{
#endif

/* user defined header files,, */
#define BFSRCH_MAX_LINE_LEN 4096

/* user defined data struct  */
typedef struct _bfsrch
{
	int  fd;
	format_t *format;

	/* for buffered read */
	char  readbuf[BFSRCH_MAX_LINE_LEN];
	char *readptr;
	int   readcnt;
} bfsrch_t;

/* user defined function  */
bfsrch_t *bfs_open(char *filename, char *lbase, char *tbase);
void bfs_close(bfsrch_t *bfs);

int bfs_nextline(bfsrch_t *bfs, char *line, int maxlen);
int bfs_readline(bfsrch_t *bfs, char *line, int maxlen);
int bfs_breadline(bfsrch_t *bfs, char *line, int maxlen);

long bfs_divide(bfsrch_t *bfs, long front, long back);
long bfs_search(bfsrch_t *bfs, time_t basetime);

int    bfs_tokenize(bfsrch_t *bfs, char *line);
time_t bfs_calctime(bfsrch_t *bfs, char *line);
void   bfs_printltk(bfsrch_t *bfs);


#ifdef __cplusplus
}  /* end extern "C" */
#endif

#endif /* _U_BFSEARCH_H_ */

