#!/bin/bash

ibps1=`npctool cnt --rx -i 0 | grep 'received bytes' | sed 's/[^0-9]*//g'`
ipps1=`npctool cnt --rx -i 0 | grep 'received frames' | sed 's/[^0-9]*//g'`
idps1=`npctool cnt --rx-queue -i 6-15 | grep Discarded | sed 's/[^0-9]*//g' | paste -sd+ | bc`
ibps2=`npctool cnt --rx -i 1 | grep 'received bytes' | sed 's/[^0-9]*//g'`
ipps2=`npctool cnt --rx -i 1 | grep 'received frames' | sed 's/[^0-9]*//g'`
idps2=`npctool cnt --rx-queue -i 16-25 | grep Discarded | sed 's/[^0-9]*//g' | paste -sd+ | bc`

sleep 1
ibps1s=`npctool cnt --rx -i 0 | grep 'received bytes' | sed 's/[^0-9]*//g'`
ipps1s=`npctool cnt --rx -i 0 | grep 'received frames' | sed 's/[^0-9]*//g'`
idps1s=`npctool cnt --rx-queue -i 6-15 | grep Discarded | sed 's/[^0-9]*//g' | paste -sd+ | bc`
ibps2s=`npctool cnt --rx -i 1 | grep 'received bytes' | sed 's/[^0-9]*//g'`
ipps2s=`npctool cnt --rx -i 1 | grep 'received frames' | sed 's/[^0-9]*//g'`
idps2s=`npctool cnt --rx-queue -i 16-25 | grep Discarded | sed 's/[^0-9]*//g' | paste -sd+ | bc`

echo "==== 100G interface stats ===="
echo " sze0.0: $(echo "scale=2; $(($ibps1s - $ibps1)) / 1024 ^3 * 8" | bc) Gbps, $(echo "scale=2; $(($ipps1s-$ipps1)) / 1024 ^2" | bc) Mpps"
if [ $ipps1s == 0 ];then
    echo "  drops: 0 pps, 0 %, 0 total"
else
    echo "  drops: $(($idps1s - $idps1)) pps, $(echo "scale=3; $(($idps1s * 100)) / $ipps1s" | bc) %, $idps1s total"
fi
echo " sze0.1: $(echo "scale=2; $(($ibps2s - $ibps2)) / 1024 ^3 * 8" | bc) Gbps, $(echo "scale=2; $(($ipps2s-$ipps2)) / 1024 ^2" | bc) Mpps"
if [ $ipps2s == 0 ];then
    echo "  drops: 0 pps, 0 %, 0 total"
else
    echo "  drops: $(($idps2s - $idps2)) pps, $(echo "scale=3; $(($idps2s * 100)) / $ipps2s" | bc) %, $idps2s total"
fi
echo "=============================="
