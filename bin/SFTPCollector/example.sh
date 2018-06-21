python SFTPCollector.py TEST conf/SFTPCollector.conf &

who > data/testsubject.csv
who > data/testsubject.dat

for ((v=0;v<10;v++)); do
	filename=data/testsubject"$v".txt
	who > $filename
	sleep 1
done

sleep 3
kill -9 $!
