/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_user.c,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#include "u_user.h"

/* the global variable */
static usertable_t  *usrtab = NULL;
static grouptable_t *grptab = NULL;

/*
 * func : compare_user_by_id
 * desc : 
 */

int compare_user_by_id(const void *v1, const void *v2) 
{
	int uid1 = ((userent_t *)v1)->uid;
	int uid2 = ((userent_t *)v2)->uid;

	return (uid1 == uid2) ? NODE_FOUND : NODE_NOT_FOUND;
}

/*
 * func : compare_user_by_name
 * desc : 
 */

int compare_user_by_name(const void *v1, const void *v2) 
{
	char *uname1 = ((userent_t *)v1)->uname;
	char *uname2 = ((userent_t *)v2)->uname;

	return !strcmp(uname1, uname2) ? NODE_FOUND : NODE_NOT_FOUND;
}

/*
 * func : compare_group_by_id
 * desc : 
 */

int compare_group_by_id(const void *v1, const void *v2) 
{
	int gid1 = ((groupent_t *)v1)->gid;
	int gid2 = ((groupent_t *)v2)->gid;

	return (gid1 == gid2) ? NODE_FOUND : NODE_NOT_FOUND;
}

/*
 * func : compare_group_by_name
 * desc : 
 */

int compare_group_by_name(const void *v1, const void *v2) 
{
	char *gname1 = ((groupent_t *)v1)->gname;
	char *gname2 = ((groupent_t *)v2)->gname;

	return !strcmp(gname1, gname2) ? NODE_FOUND : NODE_NOT_FOUND;
}

/*
 * func : uid2name
 * desc : 
 */

char *uid2name(int uid, int optimize)
{
	userent_t *ent;

	/* func name */
	printout(__F__,"uid2name");

	/* lookup... */
	ent = lookup_user_by_id(uid, optimize);
	if (!ent)
		ent = suppose_user_as_id(uid);

	return (ent) ? ent->uname : NULL;
}

/*
 * func : uname2id
 * desc : 
 */

int uname2id(char *uname, int optimize)
{
	userent_t *ent;

	/* func name */
	printout(__F__,"uname2id");

	/* lookup... */
	ent = lookup_user_by_name(uname, optimize);

	return (ent) ? ent->uid : -1;
}

/*
 * func : optimize_usertable
 * desc : 
 */

int optimize_usertable()
{
	userent_t user;
	struct passwd *pw;
	int namelen;

	/* func name */
	printout(__F__,"optimize_usertable");

	if (!usrtab)
	if ((usrtab = ll_create_node(NULL,1)) == NULL) {
		printout(__M__,"optimize_usertable: fail to create a user table");
		return -1;
	}
	
	/* lookup the passwd file */
	setpwent();
	while ((pw = getpwent()) != NULL) {
		memset(&user,0x00,sizeof(userent_t));
		namelen = strlen(pw->pw_name);
		namelen = (namelen >= MAX_UNAME_LEN) ? MAX_UNAME_LEN : namelen;

		/* set the user */
		strncpy(user.uname,pw->pw_name,namelen);
		user.uid = pw->pw_uid;
		user.gid = pw->pw_gid;

		/* search first.. */
		if (ll_search_node_data(usrtab,
					&user,
					sizeof(userent_t),
					compare_user_by_id) == NULL)
		{
			/* then insert the user info */
			ll_insert_node(usrtab,&user,sizeof(userent_t),NULL);
		}
	}

	endpwent();

	return 1;
}

/*
 * func : lookup_user_by_id
 * desc : 
 */

userent_t *lookup_user_by_id(int uid, int optimize)
{
	userent_t user;

	/* func name */
	printout(__F__,"lookup_user_by_id");

	/* checkout */
	if (!usrtab || optimize) {
		if (optimize_usertable() == -1) {
			printout(__M__,"lookup_user_by_id: fail to optimize the user table");
			return NULL;
		}
	}

	/* lookup the user */
	memset(&user,0x00,sizeof(userent_t));
	user.uid = uid;

	return (userent_t*)ll_search_node_data(usrtab,&user,sizeof(userent_t),compare_user_by_id);
}

/*
 * func : lookup_user_by_name
 * desc : 
 */

userent_t *lookup_user_by_name(char *uname, int optimize)
{
	userent_t user;

	/* func name */
	printout(__F__,"lookup_user_by_name");

	/* checkout */
	if (!usrtab || optimize) {
		if (optimize_usertable() == -1) {
			printout(__M__,"lookup_user_by_name: fail to optimize the user table");
			return NULL;
		}
	}

	/* lookup the user */
	memset(&user,0x00,sizeof(userent_t));
	snprintf(user.uname,MAX_UNAME_LEN,"%s",uname);

	return (userent_t*)ll_search_node_data(usrtab,&user,sizeof(userent_t),compare_user_by_name);
}

/*
 * func : suppose_user_as_id
 * desc : 
 */

userent_t *suppose_user_as_id(int uid)
{
	static usertable_t *table = NULL;
	userent_t user, *ent;

	/* func name */
	printout(__F__,"suppose_user_as_id");

	/* checkout table */
	if (!table)
	if ((table = ll_create_node(NULL,1)) == NULL) {
		printout(__M__,"suppose_user_as_id: fail to create a guess table");
		return NULL;
	}

	/* lookup the guessed user */
	memset(&user,0x00,sizeof(userent_t));
	user.uid = uid;
	sprintf(user.uname,"%d",uid);

	ent = (userent_t*)ll_search_node_data(table,&user,sizeof(userent_t),compare_user_by_id);
	if (!ent)
		ent = (userent_t*)ll_insert_node(table,&user,sizeof(userent_t),NULL);
	
	return ent;
}

/*
 * func : get_usertable
 * desc :
 */

usertable_t *get_usertable()
{
	/* func name */
	printout(__F__,"get_usertable");

	/* optimize first.. */
	optimize_usertable();

	return usrtab;
}

/*
 * func : gid2name
 * desc :
 */

char *gid2name(int gid, int optimize)
{
	groupent_t *ent;

	/* func name */
	printout(__F__,"gid2name");

	/* lookup... */
	ent = lookup_group_by_id(gid, optimize);
	if (!ent)
		ent = suppose_group_as_id(gid);

	return (ent) ? ent->gname : NULL;
}

/*
 * func : gname2id
 * desc :
 */

int gname2id(char *gname, int optimize)
{
	groupent_t *ent;

	/* func name */
	printout(__F__,"gname2id");

	/* lookup... */
	ent = lookup_group_by_name(gname, optimize);

	return (ent) ? ent->gid : -1;
}
 
/*
 * func : lookup_group_by_id
 * desc :
 */

groupent_t *lookup_group_by_id(int gid, int optimize)
{
	groupent_t group;

	/* func name */
	printout(__F__,"lookup_group_by_id");

	/* checkout */
	if (!grptab || optimize) {
		if (optimize_grouptable() == -1) {
			printout(__M__,"lookup_group_by_id: fail to optimize the group table");
			return NULL;
		}
	}

	/* lookup the user */
	memset(&group,0x00,sizeof(groupent_t));
	group.gid = gid;

	return (groupent_t*)ll_search_node_data(grptab,&group,sizeof(groupent_t),compare_group_by_id);
}

/*
 * func : lookup_group_by_name
 * desc :
 */

groupent_t *lookup_group_by_name(char *gname, int optimize)
{
	groupent_t group;

	/* func name */
	printout(__F__,"lookup_group_by_name");

	/* checkout */
	if (!grptab || optimize) {
		if (optimize_grouptable() == -1) {
			printout(__M__,"lookup_group_by_name: fail to optimize the group table");
			return NULL;
		}
	}

	/* lookup the group */
	memset(&group,0x00,sizeof(groupent_t));
	snprintf(group.gname,MAX_UNAME_LEN,"%s",gname);

	return (groupent_t*)ll_search_node_data(grptab,&group,sizeof(groupent_t),compare_group_by_name);
}

/*
 * func : suppose_group_as_id
 * desc :
 */

groupent_t *suppose_group_as_id(int gid)
{
	static grouptable_t *table = NULL;
	groupent_t group, *ent;

	/* func name */
	printout(__F__,"suppose_group_as_id");

	/* checkout table */
	if (!table)
	if ((table = ll_create_node(NULL,1)) == NULL) {
		printout(__M__,"suppose_group_as_id: fail to create a guess table");
		return NULL;
	}

	/* lookup the guessed group */
	memset(&group,0x00,sizeof(groupent_t));
	group.gid = gid;
	sprintf(group.gname,"%d",gid);

	ent = (groupent_t*)ll_search_node_data(table,&group,sizeof(groupent_t),compare_group_by_id);
	if (!ent)
		ent = (groupent_t*)ll_insert_node(table,&group,sizeof(groupent_t),NULL);
	
	return ent;
}
        
/*
 * func : optimize_grouptable
 * desc :
 */

int optimize_grouptable()
{
	groupent_t group;
	struct group *grp;
	int namelen;

	/* func name */
	printout(__F__,"optimize_grouptable");

	if (!grptab)
	if ((grptab = ll_create_node(NULL,1)) == NULL) {
		printout(__M__,"optimize_grouptable: fail to create a group table");
		return -1;
	}
	
	/* lookup the group file */
	setgrent();
	while ((grp = getgrent()) != NULL) {
		memset(&group,0x00,sizeof(groupent_t));
		namelen = strlen(grp->gr_name);
		namelen = (namelen >= MAX_UNAME_LEN) ? MAX_UNAME_LEN : namelen;

		/* set the user */
		strncpy(group.gname,grp->gr_name,namelen);
		group.gid = grp->gr_gid;

		/* search first.. */
		if (ll_search_node_data(grptab,
					&group,
					sizeof(groupent_t),
					compare_group_by_id) == NULL)
		{
			/* then insert the user info */
			ll_insert_node(grptab,&group,sizeof(groupent_t),NULL);
		}
	}

	endgrent();

	return 1;
}

/*
 * func : get_grouptable
 * desc :
 */

usertable_t *get_grouptable()
{
	/* func name */
	printout(__F__,"get_grouptable");

	/* optimize first.. */
	optimize_grouptable();

	return grptab;
}



