
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_tokenize.h,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#ifndef _U_TOKENIZE_H_
#define _U_TOKENIZE_H_

#include <stdio.h>
#include <stdlib.h>
#include <string.h> 
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <ctype.h>
#include <fcntl.h>

/* user defined header files,, */
#include "u_time.h"
#include "u_operate.h" /* for replace_char */
#include "u_debug.h"


#ifdef __cplusplus
extern "C" 
{
#endif

/* user defined constant list,, */
#define LINE_STAT_OK      1
#define LINE_STAT_ERR     0

#define MAX_STRING_LEN    256 
#define MAX_TOKEN_NUM     64
#define MAX_LOGNAME_LEN   256
#define MAX_LOGFORMAT_LEN 128
#define TOKEN_WS          ((char)(-1))
#define TOKEN_INDEX        '*'
#define MAX_LOGLINE_LEN   8192

#define LOADTIME_ON  1
#define LOADTIME_OFF 0

#define EATINGS '?'

enum {
	T_SIGNED = 1, 
	T_UNSIGNED, 
	T_REAL, 
	T_CHAR, 
	T_STRING,
	T_TIME
};

enum {
	N_TOTLINES = 0, 
	N_FLTLINES
};

/* user defined data structure,, */
typedef struct tokendef
{
	char word;
	int  type;
	char *desc;
} tokendef_t;

typedef struct _token
{
	char type; /* i,u,e,c,s,t */
	union {
		long   i;
		unsigned long u;
		double e;
		char   c;
		char  *s;
		time_t t;
	} value;  
} token_t;

typedef struct _tokenlst
{
	int     n;
	token_t entries[MAX_TOKEN_NUM];
} tokenlst_t;

typedef struct _format
{
	/* format strings */
	char    lfmt[MAX_LOGFORMAT_LEN];
	char    tfmt[MAX_LOGFORMAT_LEN];

	/* available token count */
	int     tknum;

	/* token identifier */
	char    word[MAX_TOKEN_NUM];
	token_t tokenlist[MAX_TOKEN_NUM]; 

	/* calculated log time */
	time_t calctime;
} format_t;

/* utility function for ltk libraies,, */
int  ischarequal(char ch1, char ch2);
int  isstrequal(char *str1, char *str2, int len);
char *nextdelimiter(char *source, char *delim, int delimsize);
char *nexttoken(char *source, char *delim, char *token, int tokensize);

int issigned(char *str);
int isunsigned(char *str);
int isreal(char *str);

/* ltk create/destroy */
format_t *ltk_format_create(char *lbase, char *tbase);
void ltk_format_destroy(format_t *format);

/* ltk utilities */
int  ltk_tokalloc(format_t *format, char *token, int index);
int  ltk_tokenize(format_t *format, char *line);

/* return member variables */
time_t   ltk_calctime(format_t *format);
token_t *ltk_tokenlist(format_t *format);

/* ltk print tokens */
void ltk_println(format_t *format, int flag);

/* etc,, */
void tokenlst_print(tokenlst_t *list);


#ifdef __cplusplus
}  /* end extern "C" */
#endif

#endif /* _U_TOKENIZE_H_ */

