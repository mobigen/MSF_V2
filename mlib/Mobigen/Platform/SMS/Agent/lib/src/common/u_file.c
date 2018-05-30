
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_file.c,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#include "u_file.h"

/*
 * func : mode2type
 * desc : file mode 를 기준으로 적절한 type char로 변환
 */

/* Return a character indicating the type of file described by
        file mode BITS:
        'd' for directories
        'D' for doors
        'b' for block special files
        'c' for character special files
        'n' for network special files
        'm' for multiplexor files
        'M' for an off-line (regular) file
        'l' for symbolic links
        's' for sockets
        'p' for fifos
        'C' for contigous data files
        '-' for regular files
        '?' for any other file type.  */

char mode2type(mode_t mode)
{
	/* func name */
	printout(__F__,"mode2type");

#ifdef S_ISBLK
	if (S_ISBLK (mode))
		return 'b';
#endif
	if (S_ISCHR (mode))
		return 'c';

	if (S_ISDIR (mode))
		return 'd';

	if (S_ISREG (mode))
		return '-';

#ifdef S_ISFIFO
	if (S_ISFIFO (mode))
		return 'p';
#endif

#ifdef S_ISLNK
	if (S_ISLNK (mode))
		return 'l';
#endif

#ifdef S_ISSOCK
	if (S_ISSOCK (mode))
		return 's';
#endif

#ifdef S_ISMPC
	if (S_ISMPC (mode))
		return 'm';
#endif

#ifdef S_ISNWK
	if (S_ISNWK (mode))
		return 'n';
#endif

#ifdef S_ISDOOR
	if (S_ISDOOR (mode))
		return 'D';
#endif

#ifdef S_ISCTG
	if (S_ISCTG (mode))
		return 'C';
#endif

	return '?';
}

/*
 * func : mode2perm_str
 * desc : file mode 를 기준으로 적절한 permission string (rwxr-xr-x) 으로 변환
 */

void mode2perm_str(mode_t mode, char *s)
{
	/* func name */
	printout(__F__,"mode2perm_str");

	/* file type.. */
	s[0] = '?';

	/* user readable check */
	if (mode & S_IRUSR)
		s[1] = 'r';
	else
		s[1] = '-';

	/* user writable check */
	if (mode & S_IWUSR)
		s[2] = 'w';
	else
		s[2] = '-';

	/* user excutable & setuid bit check */
	if (mode & S_IXUSR) {
		if (mode & S_ISUID)
			s[3] = 'S';
		else
			s[3] = 'x';
	}
	else {
		if (mode & S_ISUID)
			s[3] = 's';
		else
			s[3] = '-';
	}

	/* group readable check */
	if (mode & S_IRGRP)
		s[4] = 'r';
	else
		s[4] = '-';

	/* group writable check */
	if (mode & S_IWGRP)
		s[5] = 'w';
	else
		s[5] = '-';

	/* group excutable & setgid bit check */
	if (mode & S_IXGRP) {
		if (mode & S_ISGID)
			s[6] = 'S';
		else
			s[6] = 'x';
	}
	else {
		if (mode & S_ISGID)
			s[6] = 's';
		else
			s[6] = '-';
	}

	/* other readable check */
	if (mode & S_IROTH)
		s[7] = 'r';
	else
		s[7] = '-';

	/* other writable check */
	if (mode & S_IWOTH)
		s[8] = 'w';
	else
		s[8] = '-';
	
	/* other excutable & sticky bit check */
	if (mode & S_IXOTH) {
		if (mode & S_ISVTX)
			s[9] = 'T';
		else
			s[9] = 'x';
	}
	else {
		if (mode & S_ISVTX)
			s[9] = 't';
		else
			s[9] = '-';
	}

	/* at the end.. */
	s[PERM_STR_LEN] = '\0';

	return;
}

/*
 * func : mode2perm_str
 * desc : file mode 를 기준으로 적절한 permission string (octal format) 으로 변환
 */

void mode2perm_oct(mode_t mode, char *s)
{
	/* func name */
	printout(__F__,"mode2perm_oct");

	/* initialize octal string */
	sprintf(s,"00000");

	/* calculate.. */
	if (mode & S_ISUID)
		s[1] += 4;

	if (mode & S_ISGID)
		s[1] += 2;

	if (mode & S_ISVTX)
		s[1] += 1;

	if (mode & S_IRUSR)
		s[2] += 4;

	if (mode & S_IWUSR)
		s[2] += 2;

	if (mode & S_IXUSR)
		s[2] += 1;

	if (mode & S_IRGRP)
		s[3] += 4;

	if (mode & S_IWGRP)
		s[3] += 2;

	if (mode & S_IXGRP)
		s[3] += 1;

	if (mode & S_IROTH)
		s[4] += 4;

	if (mode & S_IWOTH)
		s[4] += 2;

	if (mode & S_IXOTH)
		s[4] += 1;

	return ;
}

/*
 * func : mode2perm
 * desc : file mode 를 기준으로 적절한 permission string 으로 변환
 */

void mode2perm(mode_t mode, char *s)
{
	/* func name */
	printout(__F__,"mode2readable");

	/* set the file permition */
	mode2perm_str(mode,s);

	/* set the file type */
	*s = mode2type(mode);

	return ;
}

/*
 * func : perm2mode
 * desc : permission string 을 mode로 변환
 */

mode_t perm2mode(char *s)
{
	mode_t mode = 0;

	/* func name */
	printout(__F__,"perm2mode");

	/* user */
	mode |= (s[1] == 'r') ? S_IRUSR : 0;
	mode |= (s[2] == 'w') ? S_IWUSR : 0;
	mode |= (s[3] == 'x') ? S_IXUSR
				: (s[3] == 's') ? S_ISUID
				: (s[3] == 'S') ? S_ISUID|S_IXUSR : 0;

	/* group */
	mode |= (s[4] == 'r') ? S_IRGRP : 0;
	mode |= (s[5] == 'w') ? S_IWGRP : 0;
	mode |= (s[6] == 'x') ? S_IXGRP
				: (s[6] == 's') ? S_ISGID
				: (s[6] == 'S') ? S_ISGID|S_IXGRP : 0;

	/* other */
	mode |= (s[7] == 'r') ? S_IROTH : 0;
	mode |= (s[8] == 'w') ? S_IWOTH : 0;
	mode |= (s[9] == 'x') ? S_IXOTH
				: (s[9] == 't') ? S_ISVTX
				: (s[9] == 'T') ? S_ISVTX|S_IXOTH : 0;

	return mode;
}

/*
 * func : u_chmod
 * desc : mode 변환
 */

int u_chmod(char *filename, char *perm)
{
	int mode, icheck;

	/* func name */
	printout(__F__,"u_chmod");

	/* perm should be a '-rwxr--r--' format */
	if ((mode = perm2mode(perm)) == -1
			|| (icheck = chmod(filename,mode)) == -1)
	{
		printout(__M__,"u_chmod: fail to chmod (%s, %s).", filename, perm); 
		return -1;
	}

	return 1;
}

/*
 * func : u_chown
 * desc : change owner & group
 */

int u_chown(char *filename, char *user, char *group)
{
	int uid = (user)  ? uname2id(user,1) : -1;
	int gid = (group) ? gname2id(group,1) : -1;

	/* change the ownership for the target file */
	if (lchown(filename,uid,gid) == -1) {
		printout(__M__,"u_chown: fail to chown (%s, %s, %s).",
							filename,
							(user) ? user : "?",
							(group) ? group : "?"); 
		return -1;
	}

	return 1;
}

/*
 * func : u_rename
 * desc : file name 변경
 */

int u_rename(char *oldone, char *newone)
{
	/* func name */
	printout(__F__,"u_rename");

	/* just call rename func */
	if (rename(oldone,newone) == -1) {
		printout(__M__,"u_rename: fail to rename %s to %s.",oldone, newone);
		return -1;
	}

	return 1;
}

/*
 * func : u_rmfile
 * desc : file 삭제
 */

int u_rmfile(char *filename)
{
	struct stat sb;

	/* func name */
	printout(__F__,"u_rmfile");

	/* check out the file stat */
	if (stat(filename,&sb) == -1) {
		printout(__M__,"u_rmfile: fail to stat %s.",filename);
		return -1;
	}

	/* check out if dir */
	if (S_ISDIR(sb.st_mode)) {
		printout(__M__,"u_rmfile: %s is a directory.",filename);
		return -1;
	}

	/* ok.. remove */
	if (unlink(filename) == -1) {
		printout(__M__,"u_rmfile: fail to unlink %s.",filename);
		return -1;
	}

	return 1;
}

/*
 * func : u_rmdir
 * desc : directory 삭제
 */

int u_rmdir(char *dirname)
{
	struct stat sb;

	/* func name */
	printout(__F__,"u_rmdir");

	/* check out the file stat */
	if (stat(dirname,&sb) == -1) {
		printout(__M__,"u_rmdir: fail to stat %s.",dirname);
		return -1;
	}

	/* check out if dir */
	if (!S_ISDIR(sb.st_mode)) {
		printout(__M__,"u_rmdir: %s is not a directory.",dirname);
		return -1;
	}

	/* ok.. remove */
	if (rmdir(dirname) == -1) {
		printout(__M__,"u_rmdir: fail to rmdir %s.",dirname);
		return -1;
	}

	return 1;
}

/*
 * func : u_rmdir_r
 * desc : directory 삭제 (with recursive manner)
 */

int u_rmdir_r(char *dirname)
{
	DIR *dir;
	struct dirent *ent;
	struct stat sb;
	int  icheck;

	/* func name */
	printout(__F__,"u_rmdir_r");

	/* open.. */
	if ((dir = opendir(dirname)) == NULL) {
		printout(__M__,"u_rmdir_r: fail to opendir %s.",dirname);
		return -1;
	}

	/* scan all.. */
	icheck = -1;
	while ((ent = readdir(dir)) != NULL) {
		char path[2048];

		/* filter.. */
		if (!strcmp(ent->d_name,".") || !strcmp(ent->d_name,".."))
			continue;

		/* set the path.. */
		memset(path,0x00,sizeof(path));
		sprintf(path,"%s%s%s", dirname,
				!strcmp(dirname,"/") ? "" : "/",
				ent->d_name);

		/* check out the file stat */
		if (lstat(path,&sb) == -1) {
			printout(__M__,"u_rmdir_r: fail to stat %s.",path);
			goto out;
		}

		/* check out if dir */
		if (S_ISDIR(sb.st_mode)) {
			if (u_rmdir_r(path) == -1) 
				goto out;
		}
		else if (u_rmfile(path) == -1) 
			goto out;

	}

	/* remove itself */
	if (u_rmdir(dirname) == -1)
		goto out;

	icheck = 1;

out:
	closedir(dir);

	return icheck;
}

/*
 * func : u_touch
 * desc : empty file 생성
 */

int u_touch(char *filename)
{
	int mode = oatoi("0644"); /* -rw-r--r-- */
	int fd;
	struct stat sb;

	/* func name */
	printout(__F__,"u_touch");
	
	/* check out if exist.. */
	errno = (lstat(filename,&sb) == -1 && errno == ENOENT) ? 0 : EEXIST;
	if (errno || (fd = open(filename, O_WRONLY|O_CREAT, mode)) == -1) 
	{
		printout(__M__,"u_touch: fail to create %s.",filename);
		return -1;
	}
	else
		close(fd); /* don't forget.. */

	return 1;
}

/*
 * func : u_touch
 * desc : empty directory 생성
 */

int u_mkdir(char *dirname)
{
	int mode = oatoi("0755"); /* -rwxr-xr-x */

	/* func name */
	printout(__F__,"u_mkdir");

	/* make dir */
	if (mkdir(dirname,mode) == -1) {
		printout(__M__,"u_mkdir: fail to mkdir %s.",dirname);
		return -1;
	}

	return 1;
}

/*
 * func : u_opendir
 * desc : directory open
 */
zdir_t *u_opendir(char *dirname)
{
	DIR *dirp;
	zdir_t *dir;

	/* func name */
	printout(__F__,"u_opendir");

	/* open directory */
	if ((dirp = opendir(dirname)) == NULL) {
		printout(__M__,"u_opendir: fail to opendir %s.",dirname);
		return NULL;
	}

	/* memory allocation */
	dir = (zdir_t *)malloc(sizeof(zdir_t));
	dir->dirname = (char *)malloc(strlen(dirname)+1);
	dir->dirent  = (zdirent_t *)malloc(sizeof(zdirent_t));

	/* initialize */
	dir->dirp = dirp;
	sprintf(dir->dirname,"%s",dirname);
	memset(dir->dirent,0x00,sizeof(zdirent_t));

	return dir;
}

/*
 * func : u_rewinddir
 * desc : directory 내용 read
 */
void u_rewinddir(zdir_t *dir)
{
	/* func name */
	printout(__F__,"u_readdir");

	rewinddir(dir->dirp);

	return ;
}

/*
 * func : u_readdir
 * desc : directory 내용 read
 */
zdirent_t *u_readdir(zdir_t *dir)
{
	struct dirent *ent;
	struct stat sb;
	char   path[2048];
	int len;

	/* func name */
	printout(__F__,"u_readdir");

	/* initialize the return value */
	memset(dir->dirent,0x00,sizeof(zdirent_t));

	/* read dir.. */
	if ((ent = readdir(dir->dirp)) == NULL) 
		return NULL;

	/* zde_name */
	len = strlen(ent->d_name);
	len = (len >= MAX_NAME_LEN) ? MAX_NAME_LEN - 1 : len;
	memcpy(dir->dirent->zde_name,ent->d_name,len);
	
	/* full path */
	sprintf(path,"%s/%s",dir->dirname,ent->d_name);

	/* let's get the file info */
	if (lstat(path,&sb) != -1) {
		memcpy(&(dir->dirent->_s),&sb,sizeof(struct stat));

		/* if this file is linked in symbolic way.. */
		if (S_ISLNK(sb.st_mode))
			readlink(path, dir->dirent->zde_link, 255);
	}

	return dir->dirent;
}

/*
 * func : u_closedir
 * desc : directory close
 */

int u_closedir(zdir_t *dir)
{
	int icheck;

	/* func name */
	printout(__F__,"u_closedir");

	if (!dir)
		return -1;

	/* release all the resource */
	icheck = closedir(dir->dirp);

	free(dir->dirname);
	free(dir->dirent);
	free(dir);

	return icheck;
}

/*
 * func : u_printdirent
 * desc : directory 내용 출력
 */

void u_printdirent(zdirent_t *ent)
{
	char perm[11];
	char timestr[20];
	char filename[1024];

	/* func name */
	printout(__F__,"u_printdirent");

	/* to a readable format */
	mode2perm(ent->zde_mode, perm);
	time2str(ent->zde_ctime,"%m월 %d일 %h:%n",timestr,sizeof(timestr));

	/* in case of symbolic linked file */
	if (S_ISLNK(ent->zde_mode)) {
		sprintf(filename,"%s -> %s", ent->zde_name, ent->zde_link);
	}
	else
		sprintf(filename,"%s", ent->zde_name);

	/* print them */
	fprintf(stderr,"%s %3d %s %5d %7ld %s %s\n",
				perm, (int)(ent->zde_nlink), uid2name(ent->zde_uid,0), 
				(int)(ent->zde_gid), ent->zde_size, timestr, filename);

	return ;
}





