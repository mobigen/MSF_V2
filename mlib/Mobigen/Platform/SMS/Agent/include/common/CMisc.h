
#ifndef __CMISC_H__
#define __CMISC_H__

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <errno.h>
#include <unistd.h>
#include <string>
#include <netdb.h>
#include <ctype.h>

/**
 * Directory scan시 필요한 구조체\n
 * 파일 정보를 저장하는 구조체.
 */
typedef struct _st_scan_dir {
    char fullpath[256];
    char filename[256];
    struct stat sbuf;
}st_scan_dir;

/**
 * 주어진 메시지를 delimeter에 의해 분리해내는 함수.
 */
int hrsplit(char *msg, char *del, char data[][1024]);
/**
 * 일반 프로세스를 데몬 프로세스로 전환하는 함수.
 *	@param 파싱할 문자열.
 *	@param delimeter.
 *	@param 파싱된 데이터가 저장될 저장소.
 *	@return 파싱된 데이터 개수.
 */
void initDaemonProc();
/**
 *	현재 시간 정보를 얻어오는 함수.
 *	@param seconds.
 *	@param micro seconds.
 */
void getTime(unsigned long *sec, unsigned long *usec);
/**
 *	sleep function for milli seconds.
 *	@param milli seconds.
 */
void msleep(unsigned long milliseconds);
/**
 *	directory scan시 파일 정령 함수.
 *	@param previous file.
 *	@param next file.
 *	@return 1 if s1 > s2, 0 if s1 == s2, -1 if s1 < s2
 */
int sortScanDir(const void *s1, const void *s2);
/**
 *	directory scan 함수.
 *	@param scan할 directory.
 *	@param scan된 directory의 파일 리스트.
 *	@param scan된 파일 리스트를 정렬하는 함수 포인터.
 *	@return scan된 파일 개수.
 */
int scanDir(char *dir, st_scan_dir **namelist, int (*handler)(const void *, const void *));
/**
 *	호스트 IP 주소를 얻어오는 함수.
 *	@param 얻어올 IP address 문자열.
 *	@return -1 if error occurred, else success.
 */
int gethostipaddr(char *haddr);
/**
 *	Shell command를 수행한 후 결과값을 얻어오는 함수.
 *	@param shell command.
 *	@param mode("r", "w", "r+", "w+", ...)
 *	@return NULL if error occurred, else return message.
 */
char *get_popen_result(char *cmd, char *mode);

#endif /* __CMISC_H__ */
