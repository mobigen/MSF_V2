/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_file.h,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#ifndef _U_FILE_H_
#define _U_FILE_H_

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>
#include <errno.h>

/* user defined headers */
#include "u_debug.h"
#include "u_missing.h"
#include "u_user.h"
#include "u_operate.h"


#ifdef __cplusplus
extern "C" 
{
#endif

/* user defined contant */
#define PERM_OCT_LEN   5
#define PERM_STR_LEN   10
#define MAX_NAME_LEN   256
#define MAX_CHKSUM_LEN 32 /* should make a extra room for a '\0' */

/* some machine doesn't define 'mode_t' type */
/* what should i do.... */
/*
#ifndef __mode_t_defined
typedef unsigned int mode_t;
#endif
*/

#define IS_UNCONCERNED_FILE(F) (!strcmp((F)->zde_name,".") || !strcmp((F)->zde_name,"..")) 

/* user defined data struct */
typedef struct _zdirent
{
	struct stat   _s; 
	char   zde_name[MAX_NAME_LEN];
	char   zde_link[MAX_NAME_LEN];
} zdirent_t;

typedef struct _zdir
{
	DIR  *dirp;
	char *dirname;
	zdirent_t *dirent;
} zdir_t;

#define zde_size   _s.st_size
#define zde_mode   _s.st_mode
#define zde_uid    _s.st_uid
#define zde_gid    _s.st_gid
#define zde_atime  _s.st_atime
#define zde_mtime  _s.st_mtime
#define zde_ctime  _s.st_ctime
#define zde_nlink  _s.st_nlink

/* user defined function */
char   mode2type(mode_t mode);
void   mode2perm_str(mode_t mode, char *s);
void   mode2perm_oct(mode_t mode, char *s);
void   mode2perm(mode_t mode, char *s);
mode_t perm2mode(char *s);

/* command implementation */
int u_chmod(char *filename, char *perm);
int u_chown(char *filename, char *user, char *group);
int u_rename(char *oldone, char *newone);
int u_rmfile(char *filename);
int u_rmdir(char *dirname);
int u_touch(char *filename);
int u_mkdir(char *dirname);

/* recursive */
int u_rmdir_r(char *dirname);

/* handle directories */
zdir_t    *u_opendir(char *dirname);
zdirent_t *u_readdir(zdir_t *dir);
void       u_rewinddir(zdir_t *dir);
int        u_closedir(zdir_t *dir);
void       u_printdirent(zdirent_t *ent);

/* file checksum */
int f2chksum(char *filename, char *chksum);


#ifdef __cplusplus
}  /* end extern "C" */
#endif

#endif



