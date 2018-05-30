
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_dlist.c,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#include "u_dlist.h"

/*
 * func : ll_create_node
 * desc : head node 생성
 */

h_node_t *ll_create_node(ll_release_fn __release, int srchflag)
{
	h_node_t *hd;
	int     icheck;

	/* func name,, */
	printout(__F__,"ll_create_node");

	icheck = 0;
	if ((hd = (h_node_t *)malloc(sizeof(h_node_t))) != NULL) {
		if ((hd->head = (d_node *)malloc(sizeof(d_node))) != NULL) {
			/* setup the links */
			hd->head->next = hd->head;
			hd->head->prev = hd->head;
			hd->head->data = NULL;

			/* setup the rest */
			ll_reset_curpos(hd);
			hd->__release = (__release) ? __release : DEFAULT_RELEASE;
			hd->count     = 0;
			hd->srchflag  = srchflag;

			icheck = 1;
		}
	}

	/* on fail, release the resources */
	if (!icheck) {
		if (hd) {
			if (hd->head) free(hd->head);
			free(hd); hd = NULL;
		}
	}

	return hd;
}

/*
 * func : ll_destory_node
 * desc : head node 할당된 resource 반환
 */

void ll_destroy_node(h_node_t **hd)
{
	/* func name,, */
	printout(__F__,"ll_destroy_node");

	/* be careful when you release the memory for head node */
	ll_delete_all_node(*hd);
	free((*hd)->head);
	free(*hd);

	*hd = (h_node_t *)NULL;
}

/*
 * func : ll_search_node
 * desc : 순차 검색
 */

d_node *ll_search_node(h_node_t *hd, void *data, int width, ll_compare_fn fcmp)
{
	d_node *node = hd->head->next;
	ll_compare_fn compare;

	/* func name,, */
	printout(__F__,"ll_search_node");

	/* setup the compare function */
	compare = (fcmp) ? fcmp : DEFAULT_COMPARE;

	/* lookup the node.. */
	while (node != hd->head) {
		if (compare(node->data, data) == NODE_FOUND)
			break;

		node = node->next;
	}

	return (node != hd->head) ? node : NULL;
}

/*
 * func : ll_search_node_data
 * desc : 검색된 실 data 반환
 */

void *ll_search_node_data(h_node_t *hd, void *data, int width, ll_compare_fn fcmp)
{
	d_node *node;

	/* func name,, */
	printout(__F__,"ll_search_node_data");

	if ((node = ll_search_node(hd, data, width, fcmp)) != NULL)
		return node->data;

	return NULL;
}

/*
 * func : ll_insertion_sort_node
 * desc : 삽입 정렬
 */

void ll_insertion_sort_node(h_node_t *hd, void *data, int width, ll_compare_fn fcmp)
{
	d_node *base = hd->head->next;
	d_node *tail = hd->head;
	d_node *pos, *nextnode;

	/* func name,, */
	printout(__F__,"ll_insertion_sort_node");

	/* oops.. no entries */
	if (base == tail) return;

	base = base->next;
	while (base != hd->head) {
		/* 1,2 or 2,3 or 3,4 ... */
		pos = base; nextnode = base->next;
		while ((pos = pos->prev) != hd->head
				&& fcmp(pos->data, base->data) > 0)
			;

		/* remove */
		base->prev->next = base->next;
		base->next->prev = base->prev;

		/* insert */
		pos->next->prev = base;
		base->next = pos->next;
		base->prev = pos;
		pos->next  = base;

		/* shift to the next node */
		base = nextnode;
	}

	return ;
}

/*
 * func : ll_merge_node
 * desc : 병합
 */

d_node *ll_merge_node(h_node_t *hd, d_node *node_1, d_node *node_2, int limits, ll_compare_fn fcmp)
{
	d_node *tnode, *tail = hd->head;
	int count_1, count_2;

	/* func name,, */
	printout(__F__,"ll_merge_node");

	count_1 = count_2 = 0;
	while (count_1 < limits && count_2 < limits && node_2 != tail) {
		if (fcmp(node_1->data, node_2->data) <= 0) {
			node_1 = node_1->next;

			/* increase the count */
			count_1++;
		}
		else {
			/* save .. */
			tnode = node_2->next;

			/* remove..  */
			node_2->prev->next = node_2->next;
			node_2->next->prev = node_2->prev;

			/* insert.. */
			node_1->prev->next = node_2;
			node_2->prev       = node_1->prev;
			node_2->next       = node_1;
			node_1->prev       = node_2;

			/* move to next */
			node_2 = tnode; /* previously saved.. */

			/* increase the count */
			count_2++;
		}
	}

	/* move the position.. */
	while (count_2 < limits && node_2 != tail) {
		node_2 = node_2->next;
		count_2++;
	}

	return node_2;
}

/*
 * func : ll_merge_sort_node
 * desc : 병합 정렬
 */

void ll_merge_sort_node(h_node_t *hd, void *data, int width, ll_compare_fn fcmp)
{
	d_node *tail = hd->head;
	d_node *node_1, *node_2;
	int bounds, count;

	/* func name,, */
	printout(__F__,"ll_merge_sort_node");

	/* set up the range.. */
	bounds = 1;

	while (bounds < hd->count) {
		/* oops.. no entries */
		if ((node_1 = hd->head->next) == tail) 
			break;

		do {
			/* calculate the start position of node_2 */
			node_2 = node_1;
			if(node_2){
			for (count = 0; count < bounds
					&& (node_2 = node_2->next) != tail; count++) ;
			}	

			/* check out if it reaches the goal.. */
			if (node_2 == tail)
				break;
		} while ((node_1 = ll_merge_node(hd, node_1, node_2, count, fcmp)) != tail);

		/* reset the lookup range */
		bounds *= 2;
	}

	return ;
}

/*
 * func : ll_merge_sort_node
 * desc : 정렬
 */

void ll_sort_node(h_node_t *hd, void *data, int width, ll_compare_fn fcmp)
{
	return ll_merge_sort_node(hd, data, width, fcmp);
}

/*
 * func : ll_insert_node_lifo
 * desc : node 추가 (last input first output)
 */

void *ll_insert_node_lifo(h_node_t *hd, void *data, int width, ll_compare_fn fcmp)
{
	d_node *node, *head = hd->head;
	int   icheck;

	/* func name,, */
	printout(__F__,"ll_insert_node_lifo");

	icheck = 0;
	if ((node = (d_node *)malloc(sizeof(d_node))) != NULL) {
		if ((node->data = (void *)malloc(width)) != NULL) {
			memcpy(node->data, data, width);
			node->width = width;

			head->next->prev = node;
			node->next = head->next; 
			node->prev = head;
			head->next = node; 

			hd->count++;
			icheck = 1;
		} else 
			free(node);
	}

	/* reset the current pointer */
	ll_reset_curpos(hd);

	return (icheck) ? node->data : NULL;
}

/*
 * func : ll_insert_node_fifo
 * desc : node 추가 (first input first output)
 */

void *ll_insert_node_fifo(h_node_t *hd, void *data, int width, ll_compare_fn fcmp)
{
	int    icheck;
	d_node *node=NULL;
	d_node *tail = (d_node *)hd->head;
	/* func name,, */
	printout(__F__,"ll_insert_node_fifo");

	icheck = 0;
	if ((node = (d_node *)malloc(sizeof(d_node))) != NULL) {
		if ((node->data = (void *)malloc(width)) != NULL) {
			memcpy(node->data, data, width);
			node->width = width;

			tail->prev->next = node;
			node->prev = tail->prev; 
			node->next = tail;
			tail->prev = node; 

			hd->count++;
			icheck = 1;
		} else 
			free(node);
	}

	/* reset the current pointer */
	ll_reset_curpos(hd);

	return (icheck) ? node->data : NULL;
}

/*
 * func : ll_insert_node_fcmp
 * desc : node 추가 (사용자 정의 방식에 따라)
 */

void *ll_insert_node_fcmp(h_node_t *hd, void *data, int width, ll_compare_fn fcmp)
{
	d_node *node, *pos, *tail = hd->head;
	int   icheck;

	/* func name,, */
	printout(__F__,"ll_insert_node_fcmp");

	icheck = 0;
	if ((node = (d_node *)malloc(sizeof(d_node))) != NULL) {
		if ((node->data = (void *)malloc(width)) != NULL) {
			memcpy(node->data, data, width);
			node->width = width;

			if ((pos = ll_search_node(hd, data, width, fcmp)) != NULL) {
				pos = pos->prev;
				pos->next->prev = node;
				node->next = pos->next;
				pos->next  = node;
				node->prev = pos;
			} else {
				/* insert node to the last */
				tail->prev->next = node;
				node->prev = tail->prev;
				node->next = tail;
				tail->prev = node;
			}

			hd->count++;
			icheck = 1;
		} else
			free(node);
	} 

	/* reset the current pointer */
	ll_reset_curpos(hd);

	return (icheck) ? node->data : NULL;
}

/*
 * func : ll_insert_node_fcmp
 * desc : node 추가 
 */

void *ll_insert_node(h_node_t *hd, void *data, int width, ll_compare_fn fcmp)
{
	/* func name,, */
	printout(__F__,"ll_insert_node");
	return ll_insert_node_fifo(hd, data, width, fcmp);
}

/*
 * func : ll_delete_all_node
 * desc : 모든 node 제거 
 */

int ll_delete_all_node(h_node_t *hd)
{
	d_node *temp, *node, *tail = hd->head;
	int    icheck;

	/* func name,, */
	printout(__F__,"ll_delete_all_node");

	temp = hd->head->next;
	while (temp != tail) {
		node = temp;
		temp = node->next;
		temp->prev = hd->head;
		hd->head->next = temp;

		/* release the node data */
		hd->__release(node->data);
		free(node);

		hd->count--;
	}

	/* reset the current pointer */
	ll_reset_curpos(hd);

	return icheck;
}

/*
 * func : ll_delete_node
 * desc : node 제거 
 */

int ll_delete_node(h_node_t *hd, void *data, int width, ll_compare_fn fcmp)
{
	d_node *node;
	int    icheck;

	/* func name,, */
	printout(__F__,"ll_delete_node");

	/* search.. */
	icheck = 1;
	if ((node = ll_search_node(hd, data, width, fcmp)) != NULL) {
		node->prev->next = node->next;
		node->next->prev = node->prev;

		/* release the node data */
		hd->__release(node->data);
		free(node);

		hd->count--;
	} 
	else
		icheck = 0;

	/* reset the current pointer */
	ll_reset_curpos(hd);

	return icheck;
}

/*
 * func : ll_element_at
 * desc : index 에 기반한 node 참조
 */

void *ll_element_at(h_node_t *hd, int at)
{
	d_node *node;

	/* func name,, */
	printout(__F__,"ll_element_at");

	if ((node = ll_element_node_at(hd,at)) != NULL)
		return node->data;

	return NULL;
}

/*
 * func : ll_element_node_at
 * desc : index 에 기반한 node 참조
 */

d_node *ll_element_node_at(h_node_t *hd, int at)
{
	d_node *node, *tail=NULL;
	int index;

	if(hd)
		tail = hd->head;
	else return NULL;


	/* func name,, */
	printout(__F__,"ll_element_node_at");

	/* idiotic missing.. */
	if (at >= hd->count) return NULL;

	if (hd->srchflag) {
		if (hd->curindex >= at) 
			ll_reset_curpos(hd);

		index = hd->curindex;
		node  = hd->curpos;

		while (node != tail) {
			if (index == at) break;
			node = node->next; 
			index++;
		}

		/* for quick search */
		hd->curindex = index;
		hd->curpos   = node;
	}
	else {
		/* initialize */
		index = 0;
		node  = hd->head->next;

		/* scan all the node */
		while (node != tail) {
			if (index == at) return node;
	
			node = node->next; 
			index++;
		}
	}

	return (node != tail) ? node : NULL;
}

/*
 * func : ll_element_node_at
 * desc : index 에 기반한 node 제거
 */

int ll_delete_at(h_node_t *hd, int at)
{
	int    icheck, index;
	d_node *tail = hd->head;
	d_node *node = hd->head->next;

	/* func name,, */
	printout(__F__,"ll_delete_at");

	/* idiotic missing.. */
	if (at >= hd->count) return 0;

	icheck = 0, index = 0;
	while (node != tail) {
		if (index == at) {
			node->prev->next = node->next;
			node->next->prev = node->prev;

			/* release the node data */
			hd->__release(node->data);
			free(node);

			hd->count--;

			break;
		}

		node = node->next; 
		index++;
	}

	/* reset the current pointer */
	ll_reset_curpos(hd);

	return icheck;
}

/*
 * func : ll_reset_curpos
 * desc : 현재 참조한 index 초기화
 */

void ll_reset_curpos(h_node_t *hd)
{
	/* func name,, */
	printout(__F__,"ll_reset_curpos");

	hd->curindex = 0;
	hd->curpos = hd->head->next;
}

/*
 * func : ll_release_data
 * desc : 실 data 에 대한 release 수행 (default)
 */
int ll_release_data(void *data)
{
	/* func name,, */
	printout(__F__,"ll_release_data");

	if (data) free(data);

	return 1;
}

/*
 * func : ll_compare_data
 * desc :
 */
int ll_compare_data(const void *d1, const void *d2)
{
	/* func name,, */
	printout(__F__,"ll_compare_data");

	return (d1 == d2) ? NODE_FOUND : NODE_NOT_FOUND ;
}

