
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_operate.c,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#include "u_operate.h"

/*
 * func : oatoi
 * desc : octal string 값을 decimal 값으로 변환
 */

int oatoi(char *s)
{
	register int o;

	/* func name,, */
	printout(__F__,"oatoi");

	if (*s == 0)
		return -1;
	for (o = 0; ISODIGIT(*s); ++s)
		o = o * 8 + *s - '0';
	if (*s)
		return -1;

	return o;
}

/*
 * func : xatoi
 * desc : hexa string 값을 decimal 값으로 변환
 */

int xatoi(char *s)
{
	register int x;

	/* func name,, */
	printout(__F__,"xatoi");

	if (*s == 0)
		return -1;
	x = 0;
	while (*s) {
		if (*s >= 'a' && *s <= 'f')
			x = x * 16 + *s - 'a' + 10;
		else if (*s >= 'A' && *s <= 'F')
			x = x * 16 + *s - 'A' + 10;
		else if (*s >= '0' && *s <= '9')
			x = x * 16 + *s - '0';
		else
			break;
		s++;
	} 

	if (*s)
		return -1;

	return x;
}

/*
 * func : page2k
 * desc : page 단위의 값을 kb 단위로 변환
 */

v_count_t page2k(v_count_t size)
{ 
	static int pgshift;
	int    t_pgsize;

	/* func name,, */
	printout(__F__,"page2k");

	if (!pgshift) {
		t_pgsize  = getpagesize();
		for ( ; t_pgsize > 1; t_pgsize >>= 1) pgshift += 1;
		pgshift -= U_LOG1024;
	}

	return (pgshift > 0) ? ((size) << pgshift) : ((size) >> (-1*pgshift));
}

/*
 * func : block2k
 * desc : block 단위의 값을 kb 단위로 변환
 */

v_count_t block2k(v_count_t size, int blocksize)
{ 
	int blockshift;

	/* func name,, */
	printout(__F__,"block2k");

	blockshift = 0;
	for ( ; blocksize > 1; blocksize >>= 1) blockshift += 1;
		blockshift -= U_LOG1024;

	return (blockshift > 0) ? ((size) << blockshift) : ((size) >> (-1*blockshift));
}

/*
 * func : getelapsed
 * desc : 경과 시간 (micro secs unit) 계산
 */

v_real_t getelapsed()
{ 
	static struct timeval prev;
	struct timeval  curr;
	struct timezone timez;
	double elapsed;

	/* func name,, */
	printout(__F__,"getelapsed");

	gettimeofday(&curr, &timez);
	elapsed = (curr.tv_sec - prev.tv_sec)
		+ (double) (curr.tv_usec - prev.tv_usec) * 1e-6; /* / 1000000.0; */

	prev.tv_sec = curr.tv_sec;
	prev.tv_usec = curr.tv_usec;

	return (elapsed);
}

/*
 * func : getelapsed_r
 * desc : 경과 시간 (micro secs unit) 계산
 */
v_real_t getelapsed_r(struct timeval *prev, int backupflag)
{ 
	struct timeval  curr;
	struct timezone timez;
	double elapsed;

	/* func name,, */
	printout(__F__,"getelapsed_r");

	gettimeofday(&curr, &timez);
	elapsed = (curr.tv_sec - prev->tv_sec)
		+ (float) (curr.tv_usec - prev->tv_usec) * 1e-6; /* / 1000000.0; */

	/* backup previous value */
	if (backupflag) {
		prev->tv_sec = curr.tv_sec;
		prev->tv_usec = curr.tv_usec;
	}

	return (elapsed);
}

/*
 * func : calcav
 * desc : 초당 평균 계산
 */
double calcav(long *nvalue, long *ovalue, long *out, double elapsed)
{
	/* func name,, */
	printout(__F__,"calcav");

	/* calculate */
	if ((*out = *ovalue - *nvalue) < 0)
		*out = (unsigned long)*nvalue - (unsigned long)*ovalue;

	/* backup the value */
	*ovalue = *nvalue;

	return (double)(*out / elapsed);
}

/*
 * func : calcav
 * desc : 초당 평균 계산
 */
double calcav64(long long *nvalue, long long *ovalue, long long *out, double elapsed)
{
	/* func name,, */
	printout(__F__,"calcav");

	/* calculate */
	if ((*out = *ovalue - *nvalue) < 0)
		*out = (unsigned long long)*nvalue - (unsigned long long)*ovalue;

	/* backup the value */
	*ovalue = *nvalue;

	return (double)(*out / elapsed);
}

/*
 * func : calcav
 * desc : 초당 평균 계산
 */
long calcpc(long *nvalue, long *ovalue, long *out, long *diff, int count)
{
	int i;
	long *lp, change, total_change;
	long half_total;

	/* func name,, */
	printout(__F__,"calcpc");

	/* initialization */
	total_change = 0;
	lp = diff;

	/* calculate changes for each state and the overall change */
	for (i = 0; i < count; i++) {
		if ((change = *nvalue - *ovalue) < 0) {
			/* this only happens when the counter wraps */
			//change = (int) ((unsigned long)*nvalue-(unsigned long)*ovalue);
			change = (int) ((unsigned long)*ovalue-(unsigned long)*nvalue);
		}

		total_change += (*lp++ = change);

		/* backup the value */
		*ovalue++ = *nvalue++;
	}

	/* to avoid divide by zero */
	total_change = (!total_change) ? 1 : total_change;

	/* calculate percentages based on overall change, rounding up */
	half_total = total_change / 2l;
	for (i = 0; i < count; i++) {
		*out++ = (long)((*diff++ * 1000 + half_total) / total_change);
	}

	/* return the total in case the caller wants to use it */
	return(total_change);
}

#if 0
/*
 * func : additions
 * desc : AVG/SECS 연산
 */

double additions(double elapsed, long *newvalue, long *oldvalue)
{
	/* double delta_per_sec; */
	long   delta;

	/* func name,, */
	printout(__F__,"additions");

	if ((delta = *oldvalue - *newvalue) < 0) 
		delta = (int)((unsigned long)*newvalue - (unsigned long)*oldvalue);

	*oldvalue = *newvalue;
	
	return (double)(delta/elapsed);
}
#endif

/*
 * func : f2b
 * desc : file 의 내용을 buffer에 저장
 */
int f2b(char *f, char *b, int size)
{
	int fd, icheck, len;

	/* func name,, */
	printout(__F__,"f2b");

	/* initialize */
	icheck = 0;

	/* dump to memory */
	if ((fd = open(f, O_RDONLY)) != -1) {
		if ((len = read(fd, b, size-1)) > 0 ) {
			b[len] = '\0';
			icheck = len;
		}
		close(fd);
	}

	return icheck;
}

/*
 * func : b2ln
 * desc : buffer 에서 한 line 을 읽어 온다. (idiotic!!)
 */
int b2ln(char *b, char *ln, int maxlen)
{
	char ch;
	int  n;

	/* func name,, */
	printout(__F__,"b2ln");

	for (n = 1; n < maxlen; n++) {
		if ((ch = *ln++ = *b++) != '\0') {
			if (ch == '\n')
				break;
		}
		else
			return 0;
	}

	*ln = '\0';

	return n;
}

/*
 * func : skip_token
 * desc : skip a token 
 */

char *skip_token(const char *p)
{
        return (skip_token_f(p));
}

char *skip_token_f(const char *p)
{
        while (isspace((int)(*p)))
                p++;
        while ( *p && !isspace((int)(*p)) )
                p++;

        return (char *)p;
}

char *skip_ws_f(const char *p)
{
        while (isspace((int)(*p)))
                p++;

        return (char *)p;
}

/*
 * func : skip_ws
 * desc : skip white space chars
 */

char *skip_ws(const char *p)
{
        return (skip_ws_f(p));
}

char *skip_ws_b(const char *p, const char *q)
{
        while ( (isspace((int)(*p)) || !(*p)) && p != q)
                p--;

        return (char *)p;
}

char *skip_token_b(const char *p, const char *q)
{
        p = skip_ws_b(p, q);
        while ( !isspace((int)(*p)) && p != q)
                p--;

        return (char *)p;
}

/*
 * func : bits_emptyset
 * desc : 32 bits size의 flag 조작
 */

void bits_emptyset(int *set)
{
	*set = 0;
}

/*
 * func : bits_fillset
 * desc : 32 bits size의 flag 조작
 */

void bits_fillset(int *set)
{
	*set = ~0;
}

/*
 * func : bits_addset
 * desc : 32 bits size의 flag 조작
 */

void bits_addset(int *set, int bits)
{
	*set |= 1 << (bits - 1);
}

/*
 * func : bits_delset
 * desc : 32 bits size의 flag 조작
 */

void bits_delset(int *set, int bits)
{
	*set &= ~(1 << (bits - 1));
}

/*
 * func : bits_isset
 * desc : 32 bits size의 flag 조작
 */

int bits_isset(int *set, int bits)
{
	return ((*set & (1 << (bits - 1))) != 0);
}

/*
 * func : trim
 * desc : trim
 */

char *trim(char *str)
{
	char *ibuf, *obuf;

	/* func name,, */
	printout(__F__,"trim");

	if (str) {
		for (ibuf = obuf = str; *ibuf; ) {
			while (*ibuf && (isspace((int)*ibuf)))
				ibuf++;
			if (*ibuf && (obuf != str))
				*(obuf++) = ' ';
			while (*ibuf && (!isspace((int)*ibuf)))
				*(obuf++) = *(ibuf++);
		}
		*obuf = '\0';
	}
		
	return (str);
}

/*
 * func : rtrim
 * desc : trim only the right side
 */

char *rtrim(char *str)
{
	int n;

	/* func name,, */
	printout(__F__,"rtrim");

	n = strlen(str) - 1;
	while (n >= 0) {
		if (!isspace((int)*(str+n))) {
			*(str+n+1) = '\0';
			break;
		}
		else
			n--;
	}

	if ((n < 0) && (isspace((int)str[0])))
		str[0] = '\0';

	return str;
}

/*
 * func : tk_count
 * desc : token 갯수를 헤아림
 */

int tk_count(char *str, char *delim)
{ 
	int icount;
	char *sp, *cp;

	/* func name,, */
	printout(__F__,"tk_count");

	if (str != NULL) {
		sp = str;
		icount = 1;
		while ((cp = strstr(sp, delim)) != NULL) {
			icount++;
			sp = cp + 1;
		}
	} else
		icount = 0;

	return icount;
}

/*
 * func : tk_space
 * desc : ?
 */

void tk_space(char **tk)
{ 
	char space = '\0';

	/* func name,, */
	printout(__F__,"tk_space");

	*tk = (char*)malloc(2);
	memset(*tk,0x00,2);
	memcpy(*tk,&space,1);
}

/*
 * func : tk_print
 * desc : token list 출력
 */

void tk_print(char **tks)
{ 
	int i;

	/* func name,, */
	printout(__F__,"tk_print");

	for (i = 0; tks[i]; i++) 
		printf("Token_%d: %s\n", i,tks[i]);
}

/*
 * func : tk_print
 * desc : token list 할당
 */

char **tk_alloc(char *from, char *delim, int *count) 
{
	int n, index, len;
	char **to = NULL;
	char *sp, *cp, *ep;

	/* func name,, */
	printout(__F__,"tk_alloc");

	if ((n = tk_count(from,delim)) != 0
			&& (to = (char **)malloc((n+1)*sizeof(char *))) != NULL) 
	{
		/* <init> */
		ep = from + strlen(from);
		sp = from;

		index = 0;

		/* loop until it scan all the tokens,, */
		while ((cp = strstr(sp,delim)) != NULL) {
			/* parse,,, */
			if ((len = cp - sp) > 0) {
				to[index] = (char*)malloc(len+1);
				memset(to[index],0x00,len+1);
				memcpy(to[index],sp,len);
			} else 
				tk_space(&to[index]);

			index++;
			sp = cp+1;
		}

		/* the last token,,, */
		if ((len = ep - sp) > 0) {
			to[index] = (char*)malloc(len+1);
			memset(to[index],0x00,len+1);
			memcpy(to[index],sp,len);
		} else
			tk_space(&to[index]);

		index++;

		/* the EOR,,, */
		to[index] = NULL;
	}

	/* the token count */
	if (count != NULL)
		*count = n;

	return (to);
}

/*
 * func : tk_release
 * desc : token list 해제
 */

void tk_release(char ***tks) 
{
	char **p;
	int i;

	/* func name,, */
	printout(__F__,"tk_release");

	if ((p = *tks) != NULL) {
		for (i = 0; p[i]; i++) free(p[i]);
		free(p);
		p = NULL;
	}

	return;
}

/*
 * func : replace_char
 * desc : 대상 character 변환
 */

void replace_char(char *str, char from, char to)
{
	int index, len;

	/* func name,, */
	printout(__F__,"replace_char");

	if (str != NULL) {
		len = strlen(str);
		for (index = 0; index < len; index++) {
			if (str[index] == from)
				str[index] = to;
		}
	}

	return;
}

/*
 * func : get_number
 * desc : 
 */

int get_number(char *numstring)
{
	int len, number;
	int isnumber;

	/* func name,, */
	printout(__F__,"get_number");

	number = -1;
	if (numstring) {
		isnumber = 1;
		len = strlen(numstring);
		while (len-- > 0) {
			if (!isdigit((int)numstring[len])) {
				isnumber = 0;
				break;
			}
		}

		/* truely number,, */
		if (isnumber)
			number = atoi(numstring);
	}

	return number;
}

/*
 * func : get_token
 * desc : 
 */

int get_token(char *line, char *token, int tokenlen)
{
	char *cp, *bp = token;

	/* func name,, */
	printout(__F__,"get_token");

	if (line && bp) {
		/* skip space,, */
		cp = line;
		while (*cp && (isspace((int)*cp)))
			cp++;

		/* alloc each charater,, */
		while (*cp && (!isspace((int)*cp)) && tokenlen-- > 0)
			*(bp++) = *(cp++);

		*bp = '\0';
	}
	
	return (token) ? strlen(token) : 0;
}

/*
 * func : hex2char
 * desc : 
 */

char hex2char(char *hex)
{
	char ch;

	/* func name,, */
	printout(__F__,"hex2char");

	return ((ch = xatoi(hex)) == (char)-1) ? '?' : ch;
}

/*
 * func : xatoa_encode
 * desc : hexa string 기반 변환
 */
int xatoa_encode(char *str, char *word, char *buf, int maxlen)
{
	int  i, icount = 0;
	char ch, *p;

	/* func name,, */
	printout(__F__,"xatoa_encode");

	/* initialize */
	p = buf; i = 0;

	/* scan all the chararters */
	while ((ch = *str++) != '\0' && (maxlen - 1) > i) {
		if (strchr(word,ch) != NULL) {
			if ((maxlen - 3) <= i)
				break;

			/* encode the target char */
			sprintf(p,"%%%02x",ch);
			p += 3; i += 2;

			/* increse the return value */
			icount += 1;
		}
		else 
			*p++ = ch;

		i++;
	}

	/* at the end of buf */
	*p = '\0';

	return (p - buf);
}

/*
 * func : xatoa_decode
 * desc : hexa string 기반 변환
 */

int xatoa_decode(char *str, char *buf, int maxlen)
{
	int i, icount = 0;
	char hex[3], ch, *p;

	/* func name,, */
	printout(__F__,"xatoa_decode");

	/* initialize */
	memset(hex,0x00,sizeof(hex));
	p = buf; i = 0;

	/* scan all the characters */
	while ((ch = *str++) != '\0' && (maxlen - 1) > i) {
		if (ch == '%') {
			if ((hex[0] = *str++) == '\0' 
					|| (hex[1] = *str++) == '\0')
				break;

			/* hex ascii to char */
			*p++ = hex2char(hex);

			/* increse the return value */
			icount += 1;
		} 
		else
			*p++ = ch;

		i++;
	}

	/* at the end of buf */
	*p = '\0';

	return (p - buf);
}

/*
 * func : mkrand
 * desc : 난수 생성 (decimal range)
 */
int mkrand()
{
        static int seed = 0;

	/* func name,, */
	printout(__F__,"mkrand");

        while (seed == 0) {
                struct timeval tp;
                gettimeofday(&tp, (struct timezone *)0);
                seed = tp.tv_usec;

                srand(seed);
        }

        return (rand());
}

/*
 * func : u_flock_r
 * desc :
 */
int u_flock_r(int fd)
{
	/* func name,, */
	printout(__F__,"u_flock_r.");

	/* lock the file */
	return lock_regular(fd, F_SETLKW, F_RDLCK, 0, SEEK_SET, 0);
}

/*
 * func : u_flock_w
 * desc :
 */
int u_flock_w(int fd)
{
	/* func name,, */
	printout(__F__,"u_flock_w.");

	/* lock the file */
	return lock_regular(fd, F_SETLKW, F_WRLCK, 0, SEEK_SET, 0);
}

/*
 * func : u_unflock
 * desc :
 */
int u_unflock(int fd)
{
	/* func */
	printout(__F__,"u_unflock");

	/* unlock the file */
	return lock_regular(fd, F_SETLK, F_UNLCK, 0, SEEK_SET, 0);
}

/*
 * func : lock_reqular
 * desc :
 */
int lock_regular(int fd, int cmd, int type, off_t offset, int whence, off_t len)
{
	struct flock    lock;

	lock.l_type   = type;   /* F_RDLCK, F_WRLCK, F_UNLCK */
	lock.l_start  = offset; /* byte offset, relative to l_whence */
	lock.l_whence = whence; /* SEEK_SET, SEEK_CUR, SEEK_END */
	lock.l_len    = len;    /* #bytes (0 means to EOF) */

	return fcntl(fd, cmd, &lock);
}


