
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_environ.c,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#include "u_environ.h"

/* global variables */
static char *Home = NULL;
static char *Path = NULL;

/*
 * func : openenv
 * desc : 설정 file open
 */
environ_t *openenv(char *filename, int oflag)
{
	environ_t *environ = NULL;
	int fd;

	/* func name,, */
	printout(__F__,"openenv");

	/* check out if the file exists */
	if ((fd = open(filename, oflag)) != -1) {
		/* initialize the environ */
		environ = (environ_t *)malloc(sizeof(environ_t));
		memset(environ,0x00,sizeof(environ_t));

		/* set the file pointer */
		environ->fd = fd;
	} else
		printout(__M__,"openenv: fail to open %s.",filename);

	return environ;
}

/*
 * func : closeenv
 * desc : 설정 file close
 */
void closeenv(environ_t *environ) 
{
	/* func name,, */
	printout(__F__,"closeenv");

	if (environ) {
		/* close the opened file */
		if (environ->fd != -1)
			close(environ->fd);

		/* release the memory */
		free(environ);
	}
}

/*
 * func : eatline
 * desc : 한 line skip
 */

void eatline(int fd)
{
	char hole;

	/* func name,, */
	printout(__F__,"eatline");

	while (read(fd, &hole, 1) == 1 && (hole != NEWLINE_CHAR))
		; /* skip until it meets newline */

	return ;
}

/*
 * func : readenv
 * desc : 설정 read
 */

char *readenv(environ_t *environ) 
{
	char ch;
	int  linesize, cc = 0;

	/* func name,, */
	printout(__F__,"readenv");

	/* makeup the line,,, */
	for (linesize = 0; linesize < MAX_LINE_SIZE; linesize++) {
again:
		if ((cc = read(environ->fd, &ch, 1)) == 1) {
			if (ch == CONTINUE_CHAR) {
				eatline(environ->fd);
				goto again;
			}
			else if (ch == COMMENT_CHAR) {
				eatline(environ->fd);
				break;
			}
			else if (ch == NEWLINE_CHAR) {
				break;
			}
			else 
				environ->line[linesize] = ch;
		}
		else if (linesize != 0) {
			break;
		}
		else
			return NULL;
	}

	if (cc == 1 && linesize == 0)
		goto again;

	environ->line[linesize] = '\0';

	return trim(environ->line);
}

/*
 * func : environlst_create
 * desc : 환경 설정
 */

environlst_t * environlst_create(char *filename, int srchflag) 
{
	environent_t entries;
	environlst_t *envlst = NULL;
	environ_t   *environ = NULL;

	/* func name,, */
	printout(__F__,"environlst_create");

	if ((environ = openenv(filename,O_RDONLY)) != NULL) {
		char *line, *cp;
		char token[MAX_LINE_SIZE+1];
		int len;

		/* create the linkedlist */
		envlst = ll_create_node(NULL, srchflag);

		/* read all the environ entries */
		while ((line = readenv(environ)) != NULL) {
			if ((cp = strstr(line, "=")) != NULL) {
				/* derive the key */
				len = cp - line;
				memset(token,0x00,sizeof(token));
				memcpy(token,line,len);
				sprintf(entries.key, "%s", trim(token));

				/* derive the value */
				if ((len =  (line + strlen(line)) - (cp+1)) < 0)
					len = 0;

				memset(token,0x00,sizeof(token));
				memcpy(token,cp+1,len);
				sprintf(entries.value, "%s", trim(token));

				/* enqueue a new entry */
				environlst_insert(envlst,&entries);
			}
		}

		/* release the file descriptor */
		closeenv(environ);
	} else
		printout(__M__,"environlst_create: fail to create the environ list.");

	return envlst;
}

/*
 * func : environlst_add
 * desc : 설정 추가
 */

void environlst_insert(environlst_t *envlst, environent_t *pentry)
{
	/* func name,, */
	printout(__F__,"environlst_insert");

	/* add new pentry */
	ll_insert_node(envlst, pentry, sizeof(environent_t), NULL);
}

/*
 * func : environlst_get
 * desc : 설정 참조
 */

char * environlst_derive(environlst_t *envlst, const char *key)
{
	environent_t *pentry;
	int at;

	/* func name,, */
	printout(__F__,"environlst_derive");

	/* loop until the key entry is found */
	at = 0;
	while ((pentry = (environent_t *)
				ll_element_at(envlst,at++)) != NULL) 
	{
		if (!strcmp(key,pentry->key))
			break;
	}

	return (pentry != NULL) ? pentry->value : NULL;
}

/*
 * func : environlst_print
 * desc : 설정 출력
 */

void environlst_print(environlst_t *envlst)
{
	environent_t *pentry;
	int at;

	/* func name,, */
	printout(__F__,"environlst_print");

	at = 0;
	while ((pentry = (environent_t *)
				ll_element_at(envlst,at++)) != NULL) 
	{
		fprintf(stderr," %s = %s\n", pentry->key, pentry->value);
	}
}

/*
 * func : environlst_destroy
 * desc : 모든 설정 제거 및 resource 반환
 */

void environlst_destroy(environlst_t *envlst)
{
	/* func name,, */
	printout(__F__,"environlst_destroy");

	ll_destroy_node(&envlst);
}

/*
 * func : gethomeenv
 * desc : HOME 참조
 */

char *gethomeenv()
{
	char *temp;
	int  len;

	/* func name,, */
	printout(__F__,"gethomeenv");

	/* check out PROGHOME */
	if (!Home) {
		if ((temp = getenv(PROGHOME)) == NULL) {
			printout(__M__,"gethomeenv: fail to getenv (%s).", PROGHOME);
			return NULL;
		}

		if ((len = strlen(temp)) < 9) {
			printout(__M__,"gethomeenv: PROGHOME (%s) is too short.", PROGHOME);
			return NULL;
		}

		if ((Home = strdup(temp)) == NULL) {
			printout(__M__,"gethomeenv: fail to strdup (no memory).");
			return NULL;
		}
	}

	return Home;
}

/*
 * func : guess_homeenv
 * desc : HOME 추측
 */

char *guess_homeenv() 
{
	return NULL;
}

/*
 * func : gethomeenv
 * desc : PATH 참조 (명령어 수행을 위한 일환)
 */

char *getpathenv()
{
	char *temp;
	int  len;

	/* func name,, */
	printout(__F__,"getpathenv");

	/* check out Home */
	if (!Home && (Home = gethomeenv()) == NULL) {
		printout(__M__,"getpathenv: fail to gethomeenv.");
		return NULL;
	}

	if (!Path) {
		len  = strlen(Home);
		len *= 2;  /* $HOME/bin, $HOME/cmd */
		len += 13; /* /bin:/cmd::. */
		           /* 123456789012 */

		if ((temp = getenv("PATH")) != NULL)
			len += strlen(temp);

		/* setup the Path */
		Path = (char *)malloc(len);
		sprintf(Path,"%s/bin:%s/cmd:%s:.",Home,Home,(temp == NULL) ? "" : temp);
	} 

	return Path;
}

/*
 * func : lookuplocation
 * desc : 실행 파일 경로 검색
 */

char *lookuplocation(char *target, char *location)
{
	char *pathenv, *cp, *sp, *ep;
	char buff[1024];
	int  icheck;

	/* func name,, */
	printout(__F__,"lookuplocation");

	if ((pathenv = getpathenv()) == NULL) 
		return NULL;

	icheck = -1;
	cp = sp = pathenv;
	ep = pathenv + strlen(pathenv);
	while (1) {
		struct stat sb;
		int len;

		cp  = strstr(sp, ":");
		len = (cp) ? cp - sp : ep - sp;
		memset(buff,0x00,sizeof(buff));
		memcpy(buff,sp,len);

		if (len > 0 && buff[len-1] == '/') 
			buff[len-1] = '\0';
		sprintf(buff,"%s/%s",buff,target);

		/* check if the file exists and is executable,, */
		if (stat(buff,&sb) != -1 
				&& !S_ISDIR(sb.st_mode)
				&& sb.st_mode & S_IXUSR) 
		{
			sprintf(location,"%s",buff);
			icheck = 1;
			break;
		}

		/* check out if the last one*/
		if (cp == NULL)
			break;

		/* to the next position */
		sp = cp + 1;
	}

	return (icheck != -1) ? location : NULL;
}


