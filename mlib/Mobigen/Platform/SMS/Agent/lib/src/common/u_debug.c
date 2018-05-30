
/*
 *
 * Copyright (C) 2004 h9mm,lbdragon. All rights reserved.
 *
 */

/*
 * @author   h9mm,lbdragon
 * @version  $Id: u_debug.c,v 1.1.1.1 2004/11/04 02:25:38 h9mm Exp $
 */

#include "u_debug.h"

/* global & static variables */
char *LevelOption = NULL;
char *NameOption  = NULL;

/*
 * func : setlvopt
 * desc : debug level 지정
 */
void setlvopt(char *level)
{
	if (LevelOption)
		free(LevelOption);

	LevelOption = strdup(level);
}

/*
 * func : setnmopt
 * desc : pname 지정
 */
void setnmopt(char *name)
{
	if (!NameOption)
		free(NameOption);

	NameOption = strdup(name);
}

/*
 * func : printout
 * desc : debug 문자열 출력
 */
void printout(const char level, const char *format, ...)
{
	va_list ap;
	char    buf[4096];

	/* check out the option */
	if (LevelOption == NULL
			|| !strchr(LevelOption,level))
		return;

	/* format strings */
	va_start(ap, format);
	vsprintf(buf, format, ap);
	va_end(ap);

	/* flush */
	if (level == __I__
			|| level == __D__ || level == __F__
			|| level == __R__ || level == __S__)
	{
		fprintf(stderr,"%s level_%c (%s_%05d) - %s\n", 
						usec2str(),
						level,
						NameOption ? NameOption : "h9mm",
						(int)getpid(),
						buf);
	}
	else {
		fprintf(stderr,"%s level_%c (%s_%05d) - %s - errno_%02d %s\n", 
						usec2str(),
						level,
						NameOption ? NameOption : "h9mm",
						(int)getpid(),
						buf,
						errno,
						strerror(errno));
	}

	fflush(stderr);

	return ;
}

/*
 * func : checkout
 * desc : 일시 정지
 */
void checkout(const char *format, ...)
{
	va_list ap;
	char    buf[4096];

	/* format strings */
	va_start(ap, format);
	vsprintf(buf, format, ap);
	va_end(ap);

	/* flush message */
	fprintf(stderr,"? Press enter to continue. [%s]\n", buf);
	fflush(stderr);

	/* eats.. */
	fgetc(stdin);

	return ;
}


