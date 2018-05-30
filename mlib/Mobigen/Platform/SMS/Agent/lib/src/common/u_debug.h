
/*
 *
 * Copyright (C) 2004 r9i9c9,lbdragon. All rights reserved.
 *
 */

/*
 * @author   r9i9c9,lbdragon
 * @version  $Id: u_debug.h,v 1.1.1.1 2004/11/04 02:25:38 r9i9c9 Exp $
 */

#ifndef _U_DEBUG_H_
#define _U_DEBUG_H_

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <stdarg.h>

/* user defined headers */
#include "u_time.h"


#ifdef __cplusplus
extern "C" 
{
#endif

/* debug key characters */
#define __E__ 'E' /* ERROR    */
#define __F__ 'F' /* FUNCTION */

#define __D__ 'D' /* DEBUG  */
#define __I__ 'I' /* INFORM */
#define __R__ 'R' /* INFORM (socket receive) */
#define __S__ 'S' /* INFORM (socket send)    */

#define __W__ 'W' /* WARNING (general)    */
#define __O__ 'O' /* WARNING (module)     */
#define __K__ 'K' /* WARNING (kernelview) */
#define __M__ 'M' /* WARNING (misc)       */

#define THIS  '?'          /* DEFAULT */
#define FULL  "EFDIRSWOKM" /* FULL    */

/* this is for a idiotic HP-UX */
#ifdef __SNPRINTF__
int snprintf(char *str, size_t size, const  char  *format, ...);
#endif

/* user defined functions */
void setlvopt(char *level);
void setnmopt(char *name);
void printout(const char c, const char *format, ...);
void checkout(const char *format, ...);


#ifdef __cplusplus
}  /* end extern "C" */
#endif

#endif



