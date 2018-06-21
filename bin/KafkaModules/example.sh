echo DATE://20180621000000 |python Producer.py TEST1 conf/Producer.conf &
sleep 2
kill -9 $!

python MessageMonitor.py TEST1 conf/MessageMonitor.conf &
sleep 2
kill -9 $!
