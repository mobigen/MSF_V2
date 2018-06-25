python example.py
echo noti://20180616000000 | python IrisSummary.py MSF_TEST conf/IS.xml tmp &
sleep 2
kill -9 $!
