
#ifndef __CKERNELCORE_H__
#define __CKERNELCORE_H__ 1
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <pthread.h>
#include <string>

#include "u_time.h"
#include "u_debug.h"
#include "u_dlist.h"
#include "u_process.h"
#include "u_operate.h"
#include "u_file.h"
#include "u_tokenize.h"
#include "u_bfsearch.h"
#include "u_user.h"

#include "sc_core.h"

//! System kernel 데이터를 조회하기 위한 interface class.
/**
 *	System kernel에 접근하기 위한 인터페이스(scCoreView) 정보를 관리하며,
 *	Multi Thread의 동시 접근을 막는 역할을 한다.
 */
class CKernelCore
{
	public:
		/** 생성자 */
		CKernelCore();
		/** 소멸자 */
		~CKernelCore();
		/**
		 *	kernel interface 구조체를 반환하는 메쏘드.
		 *	@return kernel interface pointer.
		 */
		scCoreView *getCoreView();
		/**
		 *	얻어온 kernel interface 구조체를 반납하는 메쏘드.
		 *	@param kernel interface pointer.
		 */
		void returnCoreView(scCoreView *coreview);
		/**
		 *	kernel 접근 잠금 메쏘드.
		 */
		void lock();
		/**
		 *	kernel 접근 잠금 해지 메쏘드.
		 */
		void unlock();

	private:
		scCoreView *m_coreview;	/**< kernel interface */
		pthread_mutex_t m_lock;	/**< 잠금 키 */
};

#endif /* __CKERNELCORE_H__ */
