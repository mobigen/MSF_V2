
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_time.h,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#ifndef _U_TIME_H_
#define _U_TIME_H_

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <sys/times.h>
#include <ctype.h>


#ifdef __cplusplus
extern "C" 
{
#endif

#ifdef __THREADSAFE__
#define _POSIX_PTHREAD_SEMANTICS
#endif

/* 
 * [TIME FORMAT]
 * 
 * %Y : Year (YYYY)
 * %y : Year (YY)
 * %m : Month
 * %M : Month in English
 * %d : Day
 * %h : Hour
 * %n : Minute
 * %S : Second
 */

#define MAX_TIMESTR_LEN 32

/* capacity check format 00:00:02.12345 */
char *usec2str(void);

#ifdef __THREADSAFE__
char *usec2str_r(char *str);
#endif

/* convert time (time -> string -> time) */
time_t str2time(char *format, char *str);
char  *time2str(time_t seconds, char *format, char *out, int outlen);
char  *uptime2str(time_t seconds, char *str);

/* internal util function */
void  time2chars(time_t nsec, char *year, char *month, char *day, char *hour, char *min, char *sec);
int   month_en2num(char *m);

time_t u_uptime();


#ifdef __cplusplus
}  /* end extern "C" */
#endif

#endif /* _U_TIME_H_ */


