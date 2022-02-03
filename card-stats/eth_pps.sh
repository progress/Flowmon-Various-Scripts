#!/bin/bash

time="1"     # one second
int=$1   # network interface

while true
	do
		rxpkts_old="`cat /sys/class/net/$int/statistics/rx_packets`" # recv packets
		rxdrop_old="`cat /sys/class/net/$int/statistics/rx_dropped`"
			sleep $time
                rxpkts_new="`cat /sys/class/net/$int/statistics/rx_packets`" # recv packets
		rxdrop_new="`cat /sys/class/net/$int/statistics/rx_dropped`"
		rxpkts="`expr $rxpkts_new - $rxpkts_old`"		     # evaluate expressions for recv packets
		rxdrops="`expr $rxdrop_new - $rxdrop_old`"

		if [ $rxpkts == 0 ];then
    		echo "rx 0 kpkt/s drop 0 pkt/s ( 0 %) on interface $int"
		else
    		echo "rx $(echo "scale=2; $rxpkts / 1000" | bc) kpkt/s drop $rxdrops pkt/s ($(echo "scale=3; $(($rxdrops * 100)) / $rxpkts" | bc)) %, on interface $int"
		fi
	done
