/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_tokenize.c,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#include "u_tokenize.h"

/* token list type,,, */
static tokendef_t toklist[] = {
	/* basic token list */
	{ 'i'     , T_SIGNED  , "Signed" },
	{ 'u'     , T_UNSIGNED, "Unsigned" },
	{ 'e'     , T_REAL    , "Real" },
	{ 'c'     , T_CHAR    , "Char" },
	{ 's'     , T_STRING  , "String" },
	{ 't'     , T_TIME    , "Time" },
	{ EATINGS , T_STRING  , "Eatings" },

	/* extra token list */
	{ 'T'     , T_STRING  , "Time String" },
	{ 'f'     , T_STRING  , "File" },
	{ 'H'     , T_STRING  , "Remote Host" },
	{ 'L'     , T_STRING  , "Location" },
	{ 'X'     , T_STRING  , "Target" },
	{ 'U'     , T_STRING  , "User" },
	{ 't'     , T_STRING  , "Time" },
	{ 'Y'     , T_STRING  , "Year4" },
	{ 'y'     , T_STRING  , "Year2" },
	{ 'M'     , T_STRING  , "Month in English" },
	{ 'm'     , T_STRING  , "Month" },
	{ 'd'     , T_STRING  , "Day" },
	{ 'h'     , T_STRING  , "Hour" },
	{ 'n'     , T_STRING  , "Minute" },
	{ 'S'     , T_STRING  , "Second" },
	{ 'b'     , T_SIGNED  , "Bytes" },
	{ 'o'     , T_STRING  , "Code" },
	{ 'r'     , T_STRING  , "Request" },

	/* the end of list */
	{ '\0'    , -1        , "N/A"  }
};

/*
 * func : ltk_2desc
 * desc : 
 */

char *ltk_2desc(char word)
{
	int index;

	/* func name,, */
	/* printout(__F__,"ltk_2desc"); */

	index = 0;
	while (toklist[index].word != '\0') {
		if (toklist[index].word == word)
			return toklist[index].desc;

		index++;
	}

	return toklist[index].desc; /* 'N/A' is here,, */
}

/*
 * func : ltk_2type
 * desc : 
 */

int ltk_2type(char word)
{
	int index;

	/* func name,, */
	printout(__F__,"ltk_2type");

	index = 0;
	while (toklist[index].word != '\0') {
		if (toklist[index].word == word)
			return toklist[index].type;

		index++;
	}

	return toklist[index].type;  /* '-1' is here,, */
}

/*
 * func : ltk_lformat_setup
 * desc : 
 */

int ltk_lformat_setup(format_t *format, char *lbase)
{
	char *cp, ch, word;
	int  index;

	/* func name,, */
	printout(__F__,"ltk_lformat_setup");

	/* checkout if null */
	if ((cp = lbase) == NULL) {
		printout(__M__,"ltk_lformat_setup: line base can't be NULL");
		return -1;
	}
	
	index = 0;
	format->tknum = 0;
	while ((ch = *cp++) != '\0' && index < MAX_TOKEN_NUM) {
		if (ch == '%') {
			/* setup the words */
			if ((word = *cp++) == '\0')
				break;

			format->tokenlist[format->tknum].type = ltk_2type(word);
			format->word[format->tknum] = word;
			format->lfmt[index] = TOKEN_INDEX;

			format->tknum++;
		}
		else if (isspace((int)ch)) {
			format->lfmt[index] = TOKEN_WS;
		}
		else
			format->lfmt[index] = ch;

		index++;
	}

	/* checkout */
	if (!format->tknum || index == MAX_TOKEN_NUM) {
		printout(__M__,"ltk_lformat_setup: illegal line format (%s)", lbase);
		return -1;
	}

	return 1;
}

/*
 * func : ltk_tformat_setup
 * desc : 
 */

int ltk_tformat_setup(format_t *format, char *tbase)
{
	char *cp, ch;
	int  index;

	/* func name,, */
	printout(__F__,"ltk_tformat_setup");

	/* checkout if null */
	if ((cp = tbase) == NULL) {
		printout(__M__,"ltk_tformat_setup: time base can't be NULL");
		return -1;
	}

	index = 0;
	while ((ch = *cp++) != '\0') {
		if (ch == '%') { /* %Y/%m/%d %h:%n:%S */
			if (*cp != '*' && *cp != 'Y' && *cp != 'y'
					&& *cp != 'M' && *cp != 'm'
					&& *cp != 'd' && *cp != 'h'
					&& *cp != 'n' && *cp != 'S')
			{
				printout(__M__,"ltk_tformat_setup: illegal time format (%s)",tbase);
				return -1;
			}
		}

		/* allocate the character */
		format->tfmt[index] = ch;
		index += 1;
	}

	return 1;
}

/*
 * func : ltk_format_create
 * desc : 
 */

format_t *ltk_format_create(char *lbase, char *tbase)
{
	format_t *format;
	int icheck;

	/* func name,, */
	printout(__F__,"ltk_format_create");

	/* initialize */
	format = (format_t*)malloc(sizeof(format_t));
	memset(format,0x00,sizeof(format_t));

	/* setup the line format */
	icheck = 1;
	if (ltk_lformat_setup(format, lbase) != -1) {
		/* setup the time format */
		if (tbase) 
		if (ltk_tformat_setup(format, tbase) == -1)
			icheck = -1;
	}
	else
		icheck = -1;

	/* checkout if it fails */
	if (icheck == -1) {
		free(format); format = NULL;
	}

	return format;
}

/*
 * func : ltk_format_destroy
 * desc : 
 */

void ltk_format_destroy(format_t *format)
{
	int i;

	/* func name,, */
	printout(__F__,"ltk_format_destroy");

	if (format) {
		for (i = 0; i < format->tknum; i++) {
			if ((format->tokenlist)[i].type == T_STRING
					&& (format->tokenlist)[i].value.s != NULL)
				free((format->tokenlist)[i].value.s);
		}

		free(format);
	}

	return ;
}

/*
 * func : ltk_tokalloc
 * desc : 
 */

int ltk_tokalloc(format_t *format, char *token, int index)
{
	token_t *tkp = format->tokenlist + index;
	int icheck;

	/* func name,, */
	printout(__F__,"ltk_tokalloc");

	/* set default return values,, */
	icheck = -1;

	/* select,,,, whatever,, */
	switch (tkp->type) {
		case T_SIGNED:
			if (issigned(token)) {
				tkp->value.i = atol(token);
				icheck = 1;
			}
			break;

		case T_UNSIGNED:
			if (isunsigned(token)) {
				tkp->value.u = atol(token);
				icheck = 1;
			}
			break;

		case T_REAL:
			if (isreal(token)) {
				tkp->value.e = atof(token);
				icheck = 1;
			}
			break;

		case T_CHAR:
			tkp->value.c = *token;
			icheck = 1;
			break;

		case T_STRING:
			/* release the memory first */
			if (tkp->value.s)
				free(tkp->value.s);

			/* allocate the memory */
			tkp->value.s = strdup(token);
			icheck = 1;

			break;

		case T_TIME:
			if ((format->calctime = str2time(format->tfmt, token)) != 0) {
				tkp->value.t = format->calctime;
				icheck = 1;
			}
			break;

		default:
			break;
	}
	
	return icheck;
}

/*
 * func : ltk_tokenize
 * desc : 
 */

int ltk_tokenize(format_t *format, char *line)
{
	char *f, *l, *sp;
	char token[512], delim[256];
	int  icheck, index;

	/* func name,, */
	printout(__F__,"ltk_tokenize");

	/* set return flags,, */
	icheck = 1;

	/* replace NL to NULL */
	replace_char(line, '\n', '\0');

	l = line;
	f = format->lfmt; 

	/* check the first token,,, */
	if (*f != TOKEN_INDEX)
		while (ischarequal(*f, *l)
				&& *(f++) != '\0'
				&& *(l++) != '\0'
				&& *f != TOKEN_INDEX)
			;

	/* the 'f' should be the TOKEN_INDEX,, */
	index = 0;
	if (*f == TOKEN_INDEX) {
		while (*f != '\0' && *l != '\0' && format->tknum > index) {
			/* point to next format string,, */
			sp = f+1;

			/* initialize token/delim,,, */
			memset(token,0x00,sizeof(token));
			memset(delim,0x00,sizeof(delim));

			/* read next delims,,, */
			f = nextdelimiter(sp,delim,(sizeof(delim)-1));

			/* read next tokens,,, */
			l = nexttoken(l,delim,token,(sizeof(token)-1));

			/* token allocation,, */
			if (ltk_tokalloc(format,token,index) == -1) {
				printout(__M__,
					"ltk_tokenize: the type(%c) of token(%s) is mismatch", 
					format->word[index], token);

				/* oops, error occured!! */
				icheck = -1;
				break;
			}

			index++;
		}

	} else {
		printout(__M__,"ltk_tokenize: the invalid tokens are here!");
		icheck = -1;
	}

	/* check the expected number of tokens */
	if (icheck != -1) {
		if (index != format->tknum) {
			printout(__M__, "ltk_tokenize: unexpected token count (%d/%d).", 
					index, format->tknum);

			/* oops, error occured!! */
			icheck = -1;
		} 
	}

	return icheck;
}

/*
 * func : ltk_tokenlist
 * desc : 
 */

token_t * ltk_tokenlist(format_t *format)
{
	return format->tokenlist;
}

/*
 * func : ltk_calctime
 * desc : 
 */

time_t ltk_calctime(format_t *format)
{
	return format->calctime;
}

/*
 * func : issigned
 * desc : 
 */

int issigned(char *str)
{
	char ch;

	while ((ch = *str++) != '\0') {
		if (ch != '-' && !isdigit((int)ch)) 
			return 0;
	}

	return 1;
}

/*
 * func : isunsigned
 * desc : 
 */

int isunsigned(char *str)
{
	char ch;

	while ((ch = *str++) != '\0') {
		if (!isdigit((int)ch))
			return 0;
	}

	return 1;
}

/*
 * func : isreal
 * desc : 
 */

int isreal(char *str)
{
	char ch;

	while ((ch = *str++) != '\0') {
		if (ch != '-' && ch != '.' && !isdigit((int)ch)) 
			return 0;
	}

	return 1;
}

/*
 * func : ischarequal
 * desc : 
 */

int ischarequal(char ch1, char ch2)
{
	if (ch1 == ch2
			|| (ch1 == TOKEN_WS && isspace((int)ch2))
			|| (ch2 == TOKEN_WS && isspace((int)ch1)))
		return 1;

	return 0;
}

/*
 * func : isstrequal
 * desc : 
 */

int isstrequal(char *str1, char *str2, int len)
{
	int index;

	for (index = 0; index < len; index++)
		if (!ischarequal(*(str1+index), *(str2+index)))
			return 0;

	return 1;
}

/*
 * func : nextdelimiter
 * desc : 
 */

char *nextdelimiter(char *source, char *delim, int delimsize)
{
	char ch, *cp;
	int  index;

	/* func name,, */
	printout(__F__,"nextdelimiter");

	cp = delim; index = 0;
	while ((ch = *source) != TOKEN_INDEX && ch != '\0') {
		if (delimsize > ++index) {
			*cp = ch; cp++;
		} else {
			printout(__D__, "nextdelimiter: the size(%d/%d) of delimiter is too long!!",
					index, delimsize);
		}

		source++;
	}

	/* set null the end of delimiters,,, */
	*cp = '\0';

	return source;
}

/*
 * func : nexttoken
 * desc : 
 */

char *nexttoken(char *source, char *delim, char *token, int tokensize)
{
	char ch, *cp;
	int  index, len, found;

	/* func name,, */
	printout(__F__,"nexttoken");

	len = strlen(delim); /* if len is zero, the token is the last one,, */
	found = 0; cp = token;
	for (index = 0; (ch = *source) != '\0'; index++) {
		/* allocate a current character,, */
		if (tokensize > index)
			*(cp++) = ch;
		else {
			printout(__D__, "nexttoken: the size(%d/%d)of token is too long!!",
					index, tokensize);
		}

		/* increase sources's pointer,, */
		source += 1; 

		/* check from the second one,, */
		if (len && isstrequal(source,delim,len)) {
			found = 1; break;
		}
	}

	/* set null,, */
	*cp = '\0';

	/* check if the target token is found,, */
	if (found)
		source += len;

	return source;
}

/*
 * func : ltk_println
 * desc : 
 */

void ltk_println(format_t *format, int flag)
{
	char tmstr[30];
	int  index;

	/* func name,, */
	printout(__F__,"ltk_println");

	/* loop all the token entries,, */
	for (index = 0; index < format->tknum; index++) {
		if (!flag && format->word[index] == EATINGS) {
			/* we don't care about this token,, */
			continue;
		}

		/* ok,, print tokens,, */
		fprintf(stderr, "[%16s] %2d: ", ltk_2desc(format->word[index]), index);

		switch (format->tokenlist[index].type) {
			case T_SIGNED:
				fprintf(stderr,"\"%ld\"\n", format->tokenlist[index].value.i);
				break;

			case T_UNSIGNED:
				fprintf(stderr,"\"%lu\"\n", format->tokenlist[index].value.u);
				break;

			case T_REAL:
				fprintf(stderr,"\"%f\"\n", format->tokenlist[index].value.e);
				break;

			case T_CHAR:
				fprintf(stderr,"\"%c\"\n", format->tokenlist[index].value.c);
				break;

			case T_STRING:
				fprintf(stderr,"\"%s\"\n", format->tokenlist[index].value.s);
				break;

			case T_TIME:
				time2str(format->tokenlist[index].value.t,
						"%Y/%m/%d %h:%n:%S", tmstr, sizeof(tmstr));
				fprintf(stderr,"\"%ld (%s)\"\n", 
						format->tokenlist[index].value.t, tmstr);
				break;

			default:
				fprintf(stderr,"\"N/A (%c)\"\n", format->tokenlist[index].type);
				break;
		}
	}

        return ;
}

/*
 * func : tokenlst_print
 * desc : 
 */

void tokenlst_print(tokenlst_t *tokenlst)
{
	char tmstr[20];
	int index;

	/* func name,, */
	printout(__F__,"tokenlst_print");

	/* the end of token */
	fprintf(stderr,"The Token List: ");

	for (index = 0; index < tokenlst->n; index++) {
		switch (tokenlst->entries[index].type) 
		{
		case T_SIGNED:
			fprintf(stderr,"\"%ld\" ", tokenlst->entries[index].value.i);
			break;

		case T_UNSIGNED:
			fprintf(stderr,"\"%lu\" ", tokenlst->entries[index].value.u);
			break;

		case T_REAL:
			fprintf(stderr,"\"%f\" ", tokenlst->entries[index].value.e);
			break;

		case T_CHAR:
			fprintf(stderr,"\"%c\" ", tokenlst->entries[index].value.c);
			break;

		case T_STRING:
			fprintf(stderr,"\"%s\" ", tokenlst->entries[index].value.s);
			break;

		case T_TIME:
			time2str(tokenlst->entries[index].value.t,
					"%Y/%m/%d %h:%n:%S", tmstr, sizeof(tmstr));
			fprintf(stderr,"\"%s\" ", tmstr);
			break;

		default:
			fprintf(stderr,"\"N/A (%c)\" ", tokenlst->entries[index].type);
			break;
		}
	}

	/* the end of token */
	fprintf(stderr,"\n");
}


