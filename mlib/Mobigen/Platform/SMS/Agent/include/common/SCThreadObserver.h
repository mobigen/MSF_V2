
#ifndef _SCTHREADOBSERVER_H__
#define _SCTHREADOBSERVER_H__ 1

//
// OpenThread library, Copyright (C) 2002 - 2003  The Open Thread Group
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 2.1 of the License, or (at your option) any later version.
//
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public
// License along with this library; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
//


#if __GNUC_<= 3 && defined sun

#ifdef min
#   undef min
#endif
#ifdef max
#    undef max
#endif

#endif

#include <sys/types.h>
#include <assert.h>
#include <stdio.h>
#include <iostream>
#include <vector>
#include <list>

#include <OpenThreads/Thread>
#include <OpenThreads/Mutex>
#include <OpenThreads/Barrier>
#include "ThreadObserver.h"


#include "ThreadReporter.h"

#ifdef _WIN32
#include <process.h>
#define getpid() _getpid()
#else
#include <unistd.h>
#endif 

//OpenThreads::Barrier bar;


//! Custom Thread Observer (w/finished count)

class SCThreadObserver : public ThreadObserver {

public:

    SCThreadObserver() : ThreadObserver(), _finishedCount(0) {};

    virtual ~SCThreadObserver() {};

    void threadFinished(const int threadId) {

        ThreadObserver::threadFinished(threadId);

        ++_finishedCount;
    }

    int getFinishedCount() {return _finishedCount;};


private:

    volatile int _finishedCount;

};

// check the working of OpenThreads::Thread::CurrentThread()
static OpenThreads::Thread* CurrentChecker(){
	return OpenThreads::Thread::CurrentThread();
};

#endif /* _SCTHREADOBSERVER_H__ */
