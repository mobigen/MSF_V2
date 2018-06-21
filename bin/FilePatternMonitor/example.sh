python FilePatternMonitor.py TEST conf/FilePatternMonitor.conf &
for ((v=0;v<5;v++)); do
	filename=tmp/testsubject"$v".txt
	who > $filename
	sleep 1
done
#rm -rf tmp/*
kill -9 $! 
