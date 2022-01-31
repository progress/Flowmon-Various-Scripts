#!/bin/bash

# This script is to create a file with performance stats in specific CSV format for
# Orange SK
# hostname	timestamp	dskPercent	dskPercentNode	ssCpuUser	ssCpuSystem	memTotalFree	diskIOUtilAHour	diskIOAWaitAHour	fps	udpBufferLost	flows	interfaceDrops1	interfaceDrops2	profilesNumber	channelsNumber
# nbaprobe01-ba3	2020-06-08 11:45:00	80.1	75.6	80.5	90.4	80.1	 	 	 	 	 	4302	293

# Get hostname
hs=`hostname`
# Timestamp
tsf=`date +"%Y-%m-%d-%H-%M-%S"`
ts=`date +"%Y-%m-%d %H:%M:%S"`
# Get disk utilization percentage
du=`iostat -xd | grep sda | awk '{split($0,a," "); print a[14]}'`
# disk tps
dtps=`iostat -d | grep sda | awk '{split($0,a," "); print a[2]}'`

# get disk usage
df=`df /data | tail -n 1 |  awk '{split($0,a," "); print a[5]}'`

# get disk Inode usage
di=`df -i /data | tail -n 1 |  awk '{split($0,a," "); print a[5]}'`

# CPU usage
ssCpuUser=`iostat -c | tail -2 | head -n 1 | awk '{split($0,a," "); print a[1]}'`
ssCpuSystem=`iostat -c | tail -2 | head -n 1 | awk '{split($0,a," "); print a[2]}'`
diskIOAWaitAHour=`iostat -c | tail -2 | head -n 1 | awk '{split($0,a," "); print a[4]}'`

memTotalFree=`free | grep Mem | awk '{print $7/$2 * 100.0}'`

# FPS
fps=`grep stream_architecture_report_stats /data/components/nftools/log/nfcapd.log | tail -1 | grep -Eo 'Nfcapd FPS: ([[:digit:]]+)' | sed 's/[^0-9]*//g'`

# Buffer lost
lost=/home/flowmon/perfmon/udpBufferLost
udpBufferLost=`netstat -su | grep 'receive buffer errors' | sed 's/[^0-9]*//g'`
[ ! -f "$lost" ] && echo $udpBufferLost > $lost
previous=`cat $lost`
echo $udpBufferLost > $lost
[ "$udpBufferLost" -ge "$previous" ] && udpBufferLost=$(expr $udpBufferLost - $previous)
[ $udpBufferLost == '-' ] && udpBufferLost=''

# probe
drops1=/home/flowmon/perfmon/interfaceDrops1
drops2=/home/flowmon/perfmon/interfaceDrops2
stats1=/home/flowmon/perfmon/interfaceStats1
stats2=/home/flowmon/perfmon/interfaceStats2
interfaceDrops1=`npctool cnt --rx-queue -i 6-15 | grep Discarded | sed 's/[^0-9]*//g' | paste -sd+ | bc`
[ ! -f "$drops1" ] && echo $interfaceDrops1 > $drops1
previous=`cat $drops1`
[ $interfaceDrops1 == '-' ] && interfaceDrops1=''
echo $interfaceDrops1 > $drops1
[ "$interfaceDrops1" -ge "$previous" ] && interfaceDrops1=$(expr $interfaceDrops1 - $previous)

interfaceStats1=`npctool cnt --rx -i 0 | grep 'received frames' | sed 's/[^0-9]*//g'`
[ ! -f "$stats1" ] && echo $interfaceStats1 > $stats1
previous=`cat $stats1`
[ $interfaceStats1 == '-' ] && interfaceStats1=''
echo $interfaceStats1 > $stats1
[ "$interfaceStats1" -ge "$previous" ] && interfaceStats1=$(expr $interfaceStats1 - $previous)

interfaceDrops2=`npctool cnt --rx-queue -i 16-25 | grep Discarded | sed 's/[^0-9]*//g' | paste -sd+ | bc`
echo "Observed: $interfaceDrops2"
[ ! -f "$drops2" ] && echo $interfaceDrops2 > $drops2
previous=`cat $drops2`
echo "previous: $previous"
[ $interfaceDrops2 == '-' ] && interfaceDrops2=''
echo $interfaceDrops2 > $drops2
[ "$interfaceDrops2" -ge "$previous" ] && interfaceDrops2=$(expr $interfaceDrops2 - $previous)
echo "To write: $interfaceDrops2"

interfaceStats2=`npctool cnt --rx -i 1 | grep 'received frames' | sed 's/[^0-9]*//g'`
[ ! -f "$stats2" ] && echo $interfaceStats2 > $stats2
previous=`cat $stats2`
[ $interfaceStats2 == '-' ] && interfaceStats2=''
echo $interfaceStats2 > $stats2
[ "$interfaceStats2" -ge "$previous" ] && interfaceStats2=$(expr $interfaceStats2 - $previous)

flows=`grep -e "stat pkt" /data/components/flowmonexp/log/flowmonexp.log | tail -20 | cut -d',' -f 3 | sed 's/[^0-9]*//g' | paste -sd+ | bc`

# collectors
profilesNumber=`find /data/nfsen/profiles-stat/ -name profile.dat | wc -l`
channelsNumber=`find /data/nfsen/profiles-stat/ -name *-filter.txt | wc -l`

# ADS processing on slave units
streamFps=`grep 'minIntervalFPS' /data/components/ads-stream/log/ads-license.log  | tail -1 | grep -Eo 'minIntervalFPS=([[:digit:]]+)' | sed 's/[^0-9]*//g'`

# Events in 5 minutes
adsEps=`grep "Event queue size: " /data/components/ads-psql/log/ads-output.log | tail -5 | grep -Eo '#([[:digit:]]+)' | sed 's/[^0-9]*//g' | paste -sd+ | bc`

# Data storage length in days
tend=`grep "tend = " /data/nfsen/profiles-stat/live/profile.dat | sed 's/[^0-9]*//g'`
tstart=`grep "tstart = " /data/nfsen/profiles-stat/live/profile.dat | sed 's/[^0-9]*//g'`
time=86400 # one day
tlife=$((($tend - $tstart) / $time))	

file="/home/flowmon/perfmon/"$hs"_"$tsf".csv"
echo 'hostname;timestamp;dskPercent;dskPercentNode;dskTPS;dskUtil;ssCpuUser;ssCpuSystem;diskIOAWaitAHour;memTotalFree;fps;udpBufferLost;flows;interfaceDrops1;interfaceStats1;interfaceDrops2;interfaceStats2;profilesNumber;channelsNumber;streamFps;adsEps;dataLifetime' > $file
echo "$hs;$ts;$df;$di;$dtps;$du;$ssCpuUser;$ssCpuSystem;$diskIOAWaitAHour;$memTotalFree;$fps;$udpBufferLost;$flows;$interfaceDrops1;$interfaceStats1;$interfaceDrops2;$interfaceStats2;$profilesNumber;$channelsNumber;$streamFps;$adsEps;$tlife" >> $file

