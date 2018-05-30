
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_time.c,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#include "u_time.h"
#define  SFILE "u_time"

/*
 * func : is_leapyear
 * desc : 
 */

int is_leapyear(int year)
{
	if (year%4 == 0) {
		if (year%100 == 0) {
			if (year%400 == 0) {
				return 0;
			} else
				return 1;
		} else
			return 0;
	} else
		return 1;
}

/*
 * func : daysofmonth
 * desc : 
 */

int daysofmonth(int mon, int year)
{
	if( mon == 2 ) {
		if( year%4 == 0 ) {
			if( year%100 == 0 ) {
				if( year%400 == 0 ) {
					return 29;
				} else                
					return 28;
			} else
				return 29;
		} else
			return 28;
	}

	if( mon==4 || mon==6 || mon==9 || mon==11) {
		return 30;
	} else
		return 31;
}

/*
 * func : time2chars
 * desc : 
 */

void time2chars(time_t nsec, char *year, char *month, char *day, char *hour, char *min, char *sec)
{
	struct tm  *tmp;
	time_t second;

	second = (!nsec) ? time(NULL) : nsec;
	tmp = localtime(&second);

	/* - set the argument - */
	sprintf(year , "%-4d", tmp->tm_year + 1900);
	sprintf(month, "%.2d", tmp->tm_mon + 1);
	sprintf(day  , "%.2d", tmp->tm_mday);
	sprintf(hour , "%.2d", tmp->tm_hour);
	sprintf(min  , "%.2d", tmp->tm_min);
	sprintf(sec  , "%.2d", tmp->tm_sec);

	return ;
}

/*
 * func : usec2str
 * desc : 
 */

char *usec2str(void)
{ 
	struct timeval tv;
	static char str[30];
	char *ptr;

	gettimeofday(&tv, NULL);
	ptr = ctime(&tv.tv_sec);
	strcpy(str, &ptr[11]); /* Fri Sep 13 00:00:00 1986\n\0 */
	snprintf(str+8, sizeof(str)-8, ".%06ld", tv.tv_usec);

	return(str);
}

/*
 * func : usec2str_r
 * desc : 
 */

#ifdef __THREADSAFE__
char *usec2str_r(char *str)
{ 
	struct timeval tv;
	char buf[30];

	gettimeofday(&tv, NULL);
	ctime_r(&tv.tv_sec,buf);
	strcpy(str, &buf[11]); /* Fri Sep 13 00:00:00 1986\n\0 */
	sprintf(str+8,".%06ld", tv.tv_usec);

	return(str);
}
#endif

/*
 * func : tmtksk
 * desc : 
 */
int tmtksk(char *str, char ch)
{
	char c;
	int offset;

	if (ch == 's') {
		offset = 0;
		while ((c = *(str + offset)) != '\0' && !isspace((int)c)) 
			offset++;
	}
	else if (isdigit((int)ch)) {
		offset = ch - '0';
	}
	else
		offset = 0;

	return offset;
}

/*
 * func : str2time
 * desc : 
 */

time_t str2time(char *format, char *str)
{
	time_t totday, subsec;
	char   buf[20], thisyear[5], *bp = format;
	int    offset, iyear, imonth, iday, ihour, imin, isec, loop;
	int    len;

	/* initialize */
	len    = strlen(str);
	iyear  = imonth = iday = ihour = imin = isec = 0;
	offset = 0;

	/* set current year first */
	time2str(0, "%Y", thisyear, sizeof(thisyear));
	iyear = atoi(thisyear);

	/* derive tokens */
	do {
		memset(buf, 0x00, sizeof(buf)); 

		if (*bp == '%' && *(bp+1) == 'Y') { 
			if (offset+4 > len)
				return 0;

			memcpy(buf, str+offset, 4); 

			iyear = atoi(buf); offset += 4; bp += 1;
		}
		else if (*bp == '%' && *(bp+1)== 'y') {
			if (offset+2 > len)
				return 0;

			memcpy(buf  , thisyear, 2);
			memcpy(buf+2, str+offset, 2); 

			iyear = atoi(buf); offset += 2; bp += 1;
		}
		else if (*bp == '%' && *(bp+1) == 'M') { 
			if (offset+3 > len) return 0;

			memcpy(buf, str+offset, 3); 

			imonth = month_en2num(buf); offset += 3; bp += 1;
		}
		else if (*bp == '%' && *(bp+1) == 'm') {
			if (offset+2 > len)
				return 0;

			memcpy(buf, str+offset, 2); 

			imonth = atoi(buf); offset += 2; bp += 1;
		}
		else if (*bp == '%' && *(bp+1) == 'd') {
			if (offset+2 > len)
				return 0;
			memcpy(buf,str+offset, 2); 

			iday = atoi(buf); offset += 2; bp += 1;
		}
		else if (*bp == '%' && *(bp+1) == 'h') {
			if (offset+2 > len)
				return 0;
			memcpy(buf,str+offset, 2); 

			ihour = atoi(buf); offset += 2; bp += 1;
		}
		else if (*bp == '%' && *(bp+1) == 'n') {
			if (offset+2 > len)
				return 0;

			memcpy(buf,str+offset, 2); 

			imin = atoi(buf); offset += 2; bp += 1;
		}
		else if (*bp == '%' && *(bp+1) == 'S') {
			if (offset+2 > len)
				return 0;

			memcpy(buf,str+offset, 2); 

			isec = atoi(buf); offset += 2; bp += 1;
		}
		else if (*bp == '%' && *(bp+1) == '*') {
			int n = tmtksk(str+offset, *(bp+2));

			offset += n;
			bp     += 2;
		} else
			offset++;
	} while (*bp != '\0' && *(bp += 1) != '\0');

	/* calculate the timestamp */
	totday = 0;
	for (loop = 1970; loop < iyear; loop++) 
		totday += (is_leapyear(loop) == 0) ? 366:365;

	for (loop = 1; loop < imonth; loop++) 
		totday += daysofmonth(loop, iyear);

	totday += iday-1;
	subsec = totday*(60*60*24) + ((ihour-9)*60*60) + imin*60 + isec;

	return subsec;
}

/*
 * func : time2str
 * desc : 
 */

char *time2str(time_t seconds, char *format, char *out, int outlen)
{
	char year[5],month[3],day[3],hour[3],min[3],sec[3];
	char *bp;
	int  i, j;
	
	/* initialize.. */
	memset(year ,0x00,sizeof(year));
	memset(month,0x00,sizeof(month));
	memset(day  ,0x00,sizeof(day));
	memset(hour ,0x00,sizeof(hour));
	memset(min  ,0x00,sizeof(min));
	memset(sec  ,0x00,sizeof(sec));
	memset(out  ,0x00,outlen);

	/* characters.. */
	time2chars(seconds,year,month,day,hour,min,sec);

	/* lookup '%' character.. */
	bp = format, i = 0, j = 0;
	while (i < strlen(format)) {
		if (*bp == '%' && *(bp+1) == 'Y') {
			if ((j + 4) >= outlen) break;

			memcpy(out+j, year, 4);
			j += 4, i += 2, bp += 2;
		}
		else if (*bp == '%' && *(bp+1) == 'y') {
			if ((j + 2) >= outlen) break;

			memcpy(out+j, year+2, 2);
			j += 2, i += 2, bp += 2;
		}
		else if (*bp == '%' && *(bp+1) == 'm') {
			if ((j + 2) >= outlen) break;

			memcpy(out+j, month, 2);
			j += 2, i += 2, bp += 2;
		}
		else if (*bp == '%' && *(bp+1) == 'd') {
			if ((j + 2) >= outlen) break;

			memcpy(out+j, day, 2);
			j += 2, i += 2, bp += 2;
		}
		else if (*bp == '%' && *(bp+1) == 'h') {
			if ((j + 2) >= outlen) break;

			memcpy(out+j, hour, 2);
			j += 2, i += 2, bp += 2;
		}
		else if (*bp == '%' && *(bp+1) == 'n') {
			if ((j + 2) >= outlen) break;

			memcpy(out+j, min, 2);
			j += 2, i += 2, bp += 2;
		}
		else if (*bp == '%' && *(bp+1) == 'S') {
			if ((j + 2) >= outlen) break;

			memcpy(out+j, sec, 2);
			j += 2, i += 2, bp += 2;
		} 
		else {
			if ((j + 1) >= outlen) break;

			*(out+j) = *bp;
			j += 1, i += 1, bp += 1;
		}
	}

	return out;
}

/*
 * func : uptime2str
 * desc : 
 */

char *uptime2str(time_t seconds, char *str)
{
	int ss, mm, hh, dd;
	time_t uptime;

	uptime = (seconds) ? seconds : u_uptime();

	ss = uptime % 60;
	if ((uptime - ss) > 0) {
		mm = (uptime - ss) / 60;

		if ((mm - (mm % 60)) > 0) {
			hh = (mm - (mm % 60)) / 60;
			mm = mm % 60;

			if ((hh - (hh % 24)) > 0) {
				dd = (hh - (hh % 24)) / 24;
				hh = hh % 24;
				sprintf(str, "%d days %02d:%02d:%02d", dd, hh, mm, ss);
			}
			else 
				sprintf(str, "%02d:%02d:%02d", hh, mm, ss);
		}
		else 
			sprintf(str, "%02d:%02d", mm, ss);
	}
	else 
		sprintf(str, "%02d", ss);

	return str;
}

/*
 * func : month_en2num
 * desc : 
 */

int month_en2num(char *m)
{
	int monthno = -1;

	switch (m[0]) {
		case 'A':
		case 'a':
			if ((m[1] == 'p' || m[1] == 'P') && (m[2] == 'r' || m[2] == 'R'))
				monthno = 3;
			else if ((m[1] == 'u' || m[1] == 'U') && (m[2] == 'g' || m[2] == 'G'))
				monthno = 7;
			break;
		case 'D':
		case 'd':
			if ((m[1] == 'e' || m[1] == 'E') && (m[2] == 'c' || m[2] == 'C'))
				monthno = 11;
			break;
		case 'F':
		case 'f':
			if ((m[1] == 'e' || m[1] == 'E') && (m[2] == 'b' || m[2] == 'B'))
				monthno = 1;
			break;
		case 'J':
		case 'j':
			if ((m[1] == 'a' || m[1] == 'A') && (m[2] == 'n' || m[2] == 'N'))
				monthno = 0;
			if ((m[1] == 'u' || m[1] == 'U')) {
				if ((m[2] == 'l' || m[2] == 'L'))
					monthno = 6;
				else if ((m[2] == 'n' || m[2] == 'N'))
					monthno = 5;
			}
			break;
		case 'M':
		case 'm':
			if ((m[1] == 'a' || m[1] == 'A')) {
				if ((m[2] == 'r' || m[2] == 'R'))
					monthno = 2;
				else if ((m[2] == 'y' || m[2] == 'Y'))
					monthno = 4;
			}
			break;
		case 'N':
		case 'n':
			if ((m[1] == 'o' || m[1] == 'O') && (m[2] == 'v' || m[2] == 'V'))
				monthno = 10;
			break;
		case 'O':
		case 'o':
			if ((m[1] == 'c' || m[1] == 'C') && (m[2] == 't' || m[2] == 'T'))
				monthno = 9;
			break;
		case 'S':
		case 's':
			if ((m[1] == 'e' || m[1] == 'E') && (m[2] == 'p' || m[2] == 'P'))
				monthno = 8;
			break;
	}

	return (monthno == -1) ? monthno : monthno + 1;
}

/*
 * func : u_uptime
 * desc : uptime
 */
time_t u_uptime()
{
	struct tms tbuf;
	time_t uptime;
	int    _hz = 100;

	uptime = times(&tbuf) / _hz;

	return uptime;
}



