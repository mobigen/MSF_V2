echo "System BUS test suite!!!"
echo ""
TCA localhost 9999 key1 '*' &
TCA localhost 9999 '*' key2 &
TCA localhost 9999 key1 key2 &
TCA localhost 9999 '*' '*' &
echo ""
sleep 1
echo "Register...........OK"
echo ""
sleep 10
echo ""
pkill -f TCA
echo "TCA All Kill.......OK"
echo ""
echo "Performance Test"
echo ""
TBUS-C localhost 9999 key1 key2 &
TBUS-P localhost 9999
sleep 5
echo ""
pkill -f TBUS-C
echo "Test suite END!!!"
