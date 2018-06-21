echo file://data/MSF_TEST-0-20180616000000.dat | python IrisSplitter.py COMMON conf/IrisSplitter.conf &

sleep 1
kill -9 $!
