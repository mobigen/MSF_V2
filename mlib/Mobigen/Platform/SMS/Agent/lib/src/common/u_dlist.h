
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_dlist.h,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#ifndef _U_DLIST_H_
#define _U_DLIST_H_

#include <stdio.h>
#include <stdlib.h>
#include <string.h> 
#include <unistd.h>

/* the user defined header files,, */
#include "u_debug.h"


#ifdef __cplusplus
extern "C" 
{
#endif

/* the return value from compare function */
#define NODE_FOUND     1
#define NODE_NOT_FOUND 0

/* search flag */
#define DEFAULT_SEARCH_FLAG 0
#define QUICK_SEARCH_FLAG   1

#define DEFAULT_RELEASE ll_release_data
#define DEFAULT_COMPARE ll_compare_data

/* the prototype for compare function */
typedef int (*ll_compare_fn)(const void *, const void *);
typedef int (*ll_release_fn)(void *);

/* the basic data structure for doubly linked list */
typedef struct _d_node {
	struct _d_node *next;
	struct _d_node *prev;
	int     width;
	void   *data;
} d_node;

/* the head node that contains head/tail point */
typedef struct _hd_node {
	d_node *head;
	d_node *curpos; /* current position */
	int curindex;   /* current index */
	int count;
	int srchflag;

	/* release function */
	ll_release_fn __release; 
} h_node_t;

/* create/destroy linked list */
h_node_t *ll_create_node(ll_release_fn __release, int srchflag);
void ll_destroy_node(h_node_t **hd);

/* search */
d_node *ll_search_node(h_node_t *hd, void *data, int width, ll_compare_fn fcmp);
void   *ll_search_node_data(h_node_t *hd, void *data, int width, ll_compare_fn fcmp);

/* sort */
void ll_sort_node(h_node_t *hd, void *data, int width, ll_compare_fn fcmp);
void ll_merge_sort_node(h_node_t *hd, void *data, int width, ll_compare_fn fcmp);
void ll_insertion_sort_node(h_node_t *hd, void *data, int width, ll_compare_fn fcmp);

/* insert */
void *ll_insert_node(h_node_t *hd, void *data, int width, ll_compare_fn fcmp);
void *ll_insert_node_lifo(h_node_t *hd, void *data, int width, ll_compare_fn fcmp);
void *ll_insert_node_fifo(h_node_t *hd, void *data, int width, ll_compare_fn fcmp);
void *ll_insert_node_fcmp(h_node_t *hd, void *data, int width, ll_compare_fn fcmp);

/* delete */
int ll_delete_node(h_node_t *hd, void *data, int width, ll_compare_fn fcmp);
int ll_delete_all_node(h_node_t *hd);
int ll_delete_at(h_node_t *hd, int at);

/* reference */
d_node *ll_element_node_at(h_node_t *hd, int at);
void   *ll_element_at(h_node_t *hd, int at);
void  ll_reset_curpos(h_node_t *hd);
int   ll_count_nb(h_node_t *hd);

/* default callback function */
int ll_release_data(void *data);
int ll_compare_data(const void *d1, const void *d2);



#ifdef __cplusplus
}  /* end extern "C" */
#endif

#endif /* _U_DLIST_H_ */


