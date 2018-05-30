
all:
	@make compile
	@make archive

compile:
	@make COMPILER=gnu -f makefile_pth

archive:
	#(cd pthread_src; cd `uname -s`32.Opt; ar cr ../../../../libOpenThreads.a *.o)
	#(cd pthread_src; cd `uname -s | sed 's/_.*//'`*.Opt; ar cr ../../../../libOpenThreads.a *.o)
	(cd pthread_src; cd `uname -s`*.Opt; ar cr ../../../../libOpenThreads.a *.o)


clean:
	@make clean -f makefile_pth
	@rm -f ../../libOpenThreads.a
