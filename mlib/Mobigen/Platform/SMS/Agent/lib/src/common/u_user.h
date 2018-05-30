
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_user.h,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#ifndef _U_USER_H_
#define _U_USER_H_

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string.h>
#include <dirent.h>
#include <errno.h>
#include <pwd.h>
#include <grp.h>
#include <sys/types.h>

/* user defined headers */
#include "u_debug.h"
#include "u_missing.h"
#include "u_dlist.h"


#ifdef __cplusplus
extern "C" 
{
#endif

#define MAX_UNAME_LEN 16

/* user : data struct */
typedef struct _userent
{
	int  uid;
	int  gid;
	char uname[MAX_UNAME_LEN+1];
} userent_t;

typedef h_node_t usertable_t;

/* user : function */
char *uid2name(int uid, int optimize);
int   uname2id(char *uname, int optimize);

userent_t *lookup_user_by_id(int uid, int optimize);
userent_t *lookup_user_by_name(char *uname, int optimize);
userent_t *suppose_user_as_id(int uid);

int   optimize_usertable();
usertable_t *get_usertable();

/* group : data struct */
typedef struct _groupent
{
	int  gid;
	char gname[MAX_UNAME_LEN+1];
} groupent_t;

typedef h_node_t grouptable_t;

/* group : function */
char *gid2name(int gid, int optimize);
int   gname2id(char *gname, int optimize);

groupent_t *lookup_group_by_id(int gid, int optimize);
groupent_t *lookup_group_by_name(char *gname, int optimize);
groupent_t *suppose_group_as_id(int gid);

int   optimize_grouptable();
usertable_t *get_grouptable();


#ifdef __cplusplus
}  /* end extern "C" */
#endif

#endif /* _U_USER_H_ */



