echo TEST://data/test_file.csv||2018||06 | python HiveLoader.py TEST conf/HiveLoader.conf &
sleep 2
kill -9 $!
