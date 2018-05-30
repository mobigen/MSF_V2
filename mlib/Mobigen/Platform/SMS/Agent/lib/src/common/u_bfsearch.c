
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_bfsearch.c,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#include "u_bfsearch.h"

/*
 * func : bfs_open
 * desc : 검색 대상 file open
 */

bfsrch_t *bfs_open(char *filename, char *lbase, char *tbase)
{
	bfsrch_t *bfs;
	int icheck;

	/* func name... */
	printout(__F__,"bfs_open");

	/* check out the args.. */
	if (filename == NULL
			|| lbase == NULL 
			|| tbase == NULL
			|| (bfs = (bfsrch_t*)malloc(sizeof(bfsrch_t))) == NULL)
		return NULL;

	/* intialize */
	memset(bfs,0x00,sizeof(bfsrch_t));
	icheck = -1;

	/* open the target file */
	if ((bfs->fd = open(filename, O_RDONLY)) == -1) {
		printout(__M__,"bfs_open:fail to open (%s).", filename);
		goto out;
	}

	/* create the format */
	if ((bfs->format = ltk_format_create(lbase, tbase)) == NULL) {
		printout(__M__,"bfs_open:fail to ltk_format_create (%s,%s).", lbase, tbase);
		goto out;
	}

	icheck = 1;

out:
	/* check out error */
	if (icheck == -1) {
		if (bfs->fd != -1)
			close(bfs->fd);
		if (bfs->format != NULL)
			ltk_format_destroy(bfs->format);
		free(bfs); 

		return NULL;
	}

	return bfs;
}

/*
 * func : bfs_close
 * desc : 검색 대상 file close
 */

void bfs_close(bfsrch_t *bfs)
{
	/* func name... */
	printout(__F__,"bfs_close");

	if (bfs->fd != -1)
		close(bfs->fd);

	if (bfs->format != NULL)
		ltk_format_destroy(bfs->format);

	free(bfs);
}

/*
 * func : bfs_nextline
 * desc : 한 line 을 skip, 그리고 read line
 */

int bfs_nextline(bfsrch_t *bfs, char *line, int maxlen)
{
	int n, rc;
	char c;

	/* func name,, */
	printout(__F__,"bfs_nextline");

	for(n = 1; n < maxlen ; n++) {
		if ((rc = read(bfs->fd, &c, 1)) == 1) {
			if (c == '\n')
				break;
		} else if (rc == 0) {
			if (n == 1)
				return 0;
			else
				break;
		} else if (rc < 0) 
			return -1;
	}

	return bfs_readline(bfs,line,maxlen);
}

/*
 * func : bfs_readline
 * desc : read line
 */

int bfs_readline(bfsrch_t *bfs, char *line, int maxlen)
{
	int  n,rc;
	char c, *ptr;
	ptr = line;

	/* func name,, */
	printout(__F__,"bfs_readline");

	for(n = 1; n < maxlen ; n++) {
		if ((rc = read(bfs->fd, &c, 1)) == 1 ) {
			*ptr++ = c;
			if (c == '\n')
				break;
		} else if (rc == 0) {
			if (n == 1)
				return 0;
			else
				break;
		} else if (rc < 0) {
			printout(__M__,"bfs_readline: fail to read.");
			return -1;
		}
	}

	*ptr = 0;

	return n;
}

/*
 * func : bfs_bread
 * desc : buffered 기반의 read line
 */

int bfs_bread(bfsrch_t *bfs, char *line)
{
	if (bfs->readcnt <= 0) {
again:
		/* ok, there is data to be read */
		if ((bfs->readcnt = read(bfs->fd,bfs->readbuf,BFSRCH_MAX_LINE_LEN)) < 0) {
			if (errno == EINTR)
				goto again;

			return(-1);
		}
		else if (bfs->readcnt == 0)
			return(0);

		bfs->readptr = bfs->readbuf;
	}

	bfs->readcnt--;
	*line = *bfs->readptr++;

	return(1);
}

/*
 * func : bfs_breadline
 * desc : buffered 기반의 read line
 */

int bfs_breadline(bfsrch_t *bfs, char *line, int maxlen)
{
	int  n,rc;
	char c, *ptr;
	ptr = line;

	/* func name,, */
	printout(__F__,"bfs_breadline");

	for(n = 1; n < maxlen ; n++) {
		if ((rc = bfs_bread(bfs, &c)) == 1 ) {
			*ptr++ = c;
			if (c == '\n')
				break;
		} else if (rc == 0) {
			if (n == 1)
				return 0;
			else
				break;
		} else if (rc < 0) {
			printout(__M__,"bfs_breadline: fail to read.");
			return -1;
		}
	}

	*ptr = 0;

	return n;
}

/*
 * func : bfs_printltk
 * desc : wrapper for ltk_println
 */

void bfs_printltk(bfsrch_t *bfs)
{
	ltk_println(bfs->format, 1);
}

/*
 * func : bfs_tokenize
 * desc : wrapper for ltk_tokenize
 */

int bfs_tokenize(bfsrch_t *bfs, char *line)
{
	return ltk_tokenize(bfs->format, line);
}

/*
 * func : bfs_divide
 * desc : btree 검색을 위한 이분
 */

time_t bfs_calctime(bfsrch_t *bfs, char *line)
{
	time_t calctime;

	/* func name,, */
	printout(__F__,"bfs_calctime");

	if (bfs_tokenize(bfs, line) == -1
			|| (calctime = ltk_calctime(bfs->format)) == 0)
	{
		printout(__M__,"bfs_calctime: fail to calculate the time.");
		return -1;
	}

	return calctime;
}

/*
 * func : bfs_divide
 * desc : btree 검색을 위한 이분
 */

long bfs_divide(bfsrch_t *bfs, long fr, long to)
{
	long middle;
	char c;

	/* func name,, */
	printout(__F__,"bfs_divide");

	/* calculate the middle.. */
	middle  = to - fr;
	middle /= 2;
	middle += fr;

	/* lseek.. */
	while (--middle > fr) {
		if (lseek(bfs->fd,middle,SEEK_SET) == -1) {
			printout(__M__,"bfs_divide: fail to lseek.");
			return -1;
		}

		if (read(bfs->fd,&c, 1) != 1) {
			printout(__M__,"bfs_divide: fail to read.");
			return -1;
		}

		/* ok.. i found.. */
		if (c == '\n') {
			middle += 1; /* which equals the current file offset */
			break;
		}
	}

	/* not sure it happens.. */
	if (middle < 0) middle = 0;

	/* middle is the first line,, */
	if (middle == fr && lseek(bfs->fd,middle,SEEK_SET) == -1) {
		printout(__M__,"bfs_divide: fail to lseek.");
		return -1;
	}

	return middle;
}

/*
 * func : bfs_search
 * desc : time 을 기준으로 btree 검색
 */

long bfs_search(bfsrch_t *bfs, time_t basetime)
{
	struct stat sb;
	char line[BFSRCH_MAX_LINE_LEN];
	long from, to, middle, cache, guess;
	time_t idxtime;
	int  rc, count, found;

	/* func name,, */
	printout(__F__,"bfs_search");

	/* to get the file size */
	if (fstat(bfs->fd,&sb) == -1) {
		printout(__M__,"bfs_search: fail to fstat.");
		return -1;
	}

	/* initialize */
	count = 0; cache = -1; guess = -2;
	from  = 0; to    = sb.st_size;

	/* to find target... */
	found = 0;
	while (1) {
		/* initialize */
		memset(line,0x00,sizeof(line));

		/* ok.. do jobs.. */
		if ((middle = bfs_divide(bfs,from,to)) == -1 
				|| (rc = bfs_readline(bfs, line, sizeof(line))) == -1
				|| (idxtime = bfs_calctime(bfs, line)) == -1)
		{
			/* oops.. i lost the time order.. */
			printout(__M__,"bfs_search: lost the time order.");
			return -1;
		}
		
		/* check out if the value of middle equals the previous one */ 
		if (middle == cache) {
			middle = (found) ? cache : guess;
			break;
		}

		/* compare idxtime vs. basetime */
		if (idxtime < basetime) {
			if (found) {
				middle = cache;
				break;
			}

			if (middle == 0) {
				middle = guess;
				break;
			}

			from = middle;
		}
		else { /* idxtime >= basetime */
			if (idxtime == basetime)
				found = 1;

			guess = middle;
			to    = middle;
		}

		/* setup the cache.. */
		cache = middle;
	}

	/* move the offset */
	if (middle >= 0)
		lseek(bfs->fd,middle,SEEK_SET);

	return middle;
} 


