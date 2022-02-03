#!/bin/bash

time="5"     # one second
int=$1   # network interface

while true
	do
        if ! json=$(cat "/data/components/dpdk-tools/stats/$int"); then
                continue
        fi

		rxpkts_old="`echo $json | jq '.rx_packets_ok'`" # recv packets
		rxdrop_old="`echo $json | jq '.rx_packets_drop'`"
		rxbytes_old="`echo $json | jq '.rx_bytes'`"
		sleep $time

        if ! json=$(cat "/data/components/dpdk-tools/stats/$int"); then
                continue
        fi

        rxpkts_new="`echo $json | jq '.rx_packets_ok'`" # recv packets
		rxdrop_new="`echo $json | jq '.rx_packets_drop'`"
		rxbytes_new="`echo $json | jq '.rx_bytes'`"

		rxpkts=$((($rxpkts_new - $rxpkts_old) / $time))		     # evaluate expressions for recv packets
		rxdrops=$((($rxdrop_new - $rxdrop_old) / $time))
		rxbytes=$((($rxbytes_new - $rxbytes_old) / $time))

		if [ $rxpkts == 0 ];then
    		echo "rx 0 Gbps, 0 kpps, drop 0 ppps ( 0 %) on interface $int"
		else
    		echo "rx $(echo "scale=2; $rxbytes / 1024 ^3 * 8" | bc) Gbps, $(echo "scale=2; $rxpkts / 1000" | bc) kpps, drop $rxdrops pps ($(echo "scale=3; $(($rxdrops * 100)) / $rxpkts" | bc) %), on interface $int"
		fi
	done
