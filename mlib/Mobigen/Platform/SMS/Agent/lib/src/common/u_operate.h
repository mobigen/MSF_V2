
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_operate.h,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#ifndef _U_OPERATE_H_
#define _U_OPERATE_H_

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/time.h>  /* getelapsed,,, */
#include <time.h>
#include <sys/types.h> /* file2buff */
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>     /* errno */
#include <ctype.h>

/* the user defined header files,, */
#include "u_debug.h"


#ifdef __cplusplus
extern "C" 
{
#endif

/* the user defined general data type */
typedef unsigned long      v_count_t;   /* u32 value,, */
typedef unsigned long long v_count64_t; /* u64 value,, */
typedef double             v_real_t;    /* double  value,, */

#define U_MAXBUFSIZE 4096
#define U_LOG1024      10 /* (== 2^10) */

/* will be used in oatoi */
#define ISODIGIT(c) ((c) >= '0' && (c) <= '7')

/* ascii to dec value */
int oatoi(char *s);
int xatoi(char *s);

/* number operation */
v_count_t page2k(v_count_t size);
v_count_t block2k(v_count_t size, int blocksize);
v_real_t  getelapsed();
v_real_t  getelapsed_r(struct timeval *prev_time, int backupflag);

/* calculate */
double calcav(long *nvalue, long *ovalue, long *out, double elapsed);
double calcav64(long long *nvalue, long long *ovalue, long long *out, double elapsed);
long   calcpc(long *nvalue, long *ovalue, long *out, long *diff, int count);

/* file parsing and tokenization */
int f2b(char *f, char *b, int size);
int b2ln(char *b, char *ln, int maxlen);

char *skip_token(const char *p);
char *skip_ws(const char *p);
char *skip_token_f(const char *p);
char *skip_ws_f(const char *p);
char *skip_ws_b(const char *p, const char *q);
char *skip_token_b(const char *p, const char *q);

/* trim */
char *trim(char *str);
char *rtrim(char *str);

/* charater tokenization */
char **tk_alloc(char *from, char *delim, int *count);
int  tk_count(char *from, char *delim);
void tk_release(char ***tks);
void tk_print(char **tks);

/* convert char */
void replace_char(char *str, char from, char to);

/* bit operation */
void bits_emptyset(int *set);
void bits_fillset(int *set);
void bits_addset(int *set, int bits);
void bits_delset(int *set, int bits);
int  bits_isset(int *set, int bits);

/* encode/decode hexa value */
int xatoa_encode(char *str, char *word, char *buf, int maxlen);
int xatoa_decode(char *str, char *buf, int maxlen);

/* make the random */
int mkrand();

/* file locking */
int u_flock_r(int fd);
int u_flock_w(int fd);
int u_unflock(int fd);
int lock_regular(int fd, int cmd, int type, off_t offset, int whence, off_t len);


#ifdef __cplusplus
}  /* end extern "C" */
#endif

#endif /* _U_OPERATE_H_ */






