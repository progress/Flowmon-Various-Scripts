#!/bin/bash

# This script is to create a file with performance stats in specific Prometheus format
# https://prometheus.io/docs/instrumenting/exposition_formats/
# It will be used then by node_exporter Textfile Collector
# https://github.com/prometheus/node_exporter

# Number of exporters running
exporters=1
# number of listening ports
lis_ports=2
# is ADS installed
if grep -Fq "ADS" /etc/flowmon/license;
then
    ads=1
else
    ads=0
fi
# is this a probe
if head -n 1 /etc/flowmon/license | grep -Fq "Flowmon Probe";
then
    probe=1
else
    probe=0
fi
# is this a proxy unit?
if head -n 1 /etc/flowmon/license | grep -q "Proxy";
then
    proxy=1
else
    proxy=0
fi

# probe
if [ $probe -gt 0 ]; then
    mellanox=`lspci | grep "Ethernet controller: Mellanox Technologies" | wc -l`
    netcope=`lspci | grep "Ethernet controller: Netcope Technologies" | wc -l`
    if [ $netcope -gt 0 ]; then 
        interfaceDrops1=`npctool cnt --rx-queue -i 6-15 | grep Discarded | sed 's/[^0-9]*//g' | paste -sd+ | bc`
        interfaceStats1=`npctool cnt --rx -i 0 | grep 'received frames' | sed 's/[^0-9]*//g'`
        interfaceDrops2=`npctool cnt --rx-queue -i 16-25 | grep Discarded | sed 's/[^0-9]*//g' | paste -sd+ | bc`
        interfaceStats2=`npctool cnt --rx -i 1 | grep 'received frames' | sed 's/[^0-9]*//g'`
        flows=`grep -e "stat pkt" /data/components/flowmonexp/log/flowmonexp.log | tail -$exporters | cut -d',' -f 3 | sed 's/[^0-9]*//g' | paste -sd+ | bc`
        exp_bytes=`grep -e "stat pkt" /data/components/flowmonexp/log/flowmonexp.log | tail -$exporters | cut -d',' -f 2 | sed 's/[^0-9]*//g' | paste -sd+ | bc`
        exp_packets=`grep -e "stat pkt" /data/components/flowmonexp/log/flowmonexp.log | tail -$exporters | cut -d',' -f 1 | grep -Eo '    ([[:digit:]]+)' | sed 's/[^0-9]*//g' | paste -sd+ | bc`
        flows_merged=`grep -e "stat pkt" /data/components/flowmonexp/log/flowmonexp.log | tail -$exporters | cut -d',' -f 4 | sed 's/[^0-9]*//g' | paste -sd+ | bc`
        flows_queued=`grep -e "stat pkt" /data/components/flowmonexp/log/flowmonexp.log | tail -$exporters | cut -d',' -f 5 | sed 's/[^0-9]*//g' | paste -sd+ | bc`
        collisions=`grep -e "stat pkt" /data/components/flowmonexp/log/flowmonexp.log | tail -$exporters | cut -d',' -f 6 | sed 's/[^0-9]*//g' | paste -sd+ | bc`
    else
        if [ $mellanox -gt 0 ]; then
            json1=$(cat "/data/components/dpdk-tools/stats/eth4")
            json2=$(cat "/data/components/dpdk-tools/stats/eth6")
            interfaceDrops1="`echo $json1 | jq '.rx_packets_drop'`"
            interfaceStats1="`echo $json1 | jq '.rx_packets_ok'`"
            interfaceDrops2="`echo $json2 | jq '.rx_packets_drop'`"
            interfaceStats2="`echo $json2 | jq '.rx_packets_ok'`"
            flows=`grep -e "total stat pkt   " /data/components/flowmonexp/log/flowmonexp.log | tail -1 | cut -d',' -f 3 | sed 's/[^0-9]*//g'`
            exp_bytes=`grep -e "total stat pkt" /data/components/flowmonexp/log/flowmonexp.log | tail -1 | cut -d',' -f 2 | sed 's/[^0-9]*//g' | paste -sd+ | bc`
            exp_packets=`grep -e "total stat pkt" /data/components/flowmonexp/log/flowmonexp.log | tail -1 | cut -d',' -f 1 | grep -Eo '    ([[:digit:]]+)' | sed 's/[^0-9]*//g' | paste -sd+ | bc`
            flows_merged=0
            flows_queued=`grep -e "total stat pkt" /data/components/flowmonexp/log/flowmonexp.log | tail -1 | cut -d',' -f 4 | sed 's/[^0-9]*//g' | paste -sd+ | bc`
            collisions=`grep -e "total stat pkt" /data/components/flowmonexp/log/flowmonexp.log | tail -1 | cut -d',' -f 5 | sed 's/[^0-9]*//g' | paste -sd+ | bc`
        else
            if [ -f "/data/components/flowmonexp/log/flowmonexp.log" ]; then
                interfaceDrops1=0
                interfaceStats1=0
                interfaceDrops2=0
                interfaceStats2=0
                flows=`grep -e "stat pkt" /data/components/flowmonexp/log/flowmonexp.log | tail -$exporters | cut -d',' -f 3 | sed 's/[^0-9]*//g' | paste -sd+ | bc`
                exp_bytes=`grep -e "stat pkt" /data/components/flowmonexp/log/flowmonexp.log | tail -$exporters | cut -d',' -f 2 | sed 's/[^0-9]*//g' | paste -sd+ | bc`
                exp_packets=`grep -e "stat pkt" /data/components/flowmonexp/log/flowmonexp.log | tail -$exporters | cut -d',' -f 1 | grep -Eo '    ([[:digit:]]+)' | sed 's/[^0-9]*//g' | paste -sd+ | bc`
                flows_merged=`grep -e "stat pkt" /data/components/flowmonexp/log/flowmonexp.log | tail -$exporters | cut -d',' -f 4 | sed 's/[^0-9]*//g' | paste -sd+ | bc`
                flows_queued=`grep -e "stat pkt" /data/components/flowmonexp/log/flowmonexp.log | tail -$exporters | cut -d',' -f 5 | sed 's/[^0-9]*//g' | paste -sd+ | bc`
                collisions=`grep -e "stat pkt" /data/components/flowmonexp/log/flowmonexp.log | tail -$exporters | cut -d',' -f 6 | sed 's/[^0-9]*//g' | paste -sd+ | bc`
            else
                interfaceDrops1=0
                interfaceStats1=0
                interfaceDrops2=0
                interfaceStats2=0
                flows=0
                exp_bytes=0
                exp_packets=0
                flows_merged=0
                flows_queued=0
                collisions=0
            fi
        fi
    fi
fi

# collectors
if [ $proxy -eq 0 ]; then
    profilesNumber=`find /data/nfsen/profiles-stat/ -name profile.dat | wc -l`
    channelsNumber=`find /data/nfsen/profiles-stat/ -name *-filter.txt | wc -l`

    # FPS collector
    fps=`grep stream_architecture_report_stats /data/components/nftools/log/nfcapd.log | tail -$lis_ports | grep -Eo 'Nfcapd FPS: ([[:digit:]]+)' | sed 's/[^0-9]*//g' | paste -sd+ | bc`   

    # Data storage length in days
    tend=`grep "tend = " /data/nfsen/profiles-stat/live/profile.dat | sed 's/[^0-9]*//g'`
    tstart=`grep "tstart = " /data/nfsen/profiles-stat/live/profile.dat | sed 's/[^0-9]*//g'`
    time=86400 # one day
    tlife=$((($tend - $tstart) / $time))	
else
    # FPS seen on proxy unit
    fps=`grep nfcapd /data/components/nftools/log/nfcapd.log | tail -$lis_ports | grep -Eo 'flows_ps:([[:digit:]]+)' | sed 's/[^0-9]*//g' | paste -sd+ | bc`
fi

if [ $ads -gt 0 ]; then
    # ADS processing on slave units
    if [ -f "/data/components/ads-stream/log/ads-license.log" ]; then
        streamFps=`grep 'minIntervalFPS' /data/components/ads-stream/log/ads-license.log  | tail -1 | grep -Eo 'minIntervalFPS=([[:digit:]]+)' | sed 's/[^0-9]*//g'`
    else
        streamFps=0
    fi

    # Events in 5 minutes
    if [ -f "/data/components/ads-psql/log/ads-output.log" ]; then
        adsEps=`grep "Event queue size: " /data/components/ads-psql/log/ads-output.log | tail -5 | grep -Eo '#([[:digit:]]+)' | sed 's/[^0-9]*//g' | paste -sd+ | bc`
    else
        adsEps=0
    fi
fi

file="/home/flowmon/perfmon/node-exporter.prom"
echo "# Contains various Flowmon specific metrics to use in node-exporter" > $file

echo "# HELP nfcapd_flows Number of flows received by the collector" >> $file
echo "# TYPE nfcapd_flows gauge" >> $file
echo "nfcapd_flows $fps" >> $file

if [ $probe -gt 0 ]; then
    echo "# HELP flowmonexp_flows Number of flows created by the exporter" >> $file
    echo "# TYPE flowmonexp_flows gauge" >> $file
    echo "flowmonexp_flows $flows" >> $file
    echo "# HELP flowmonexp_bytes Number of bytes processed by the exporter" >> $file
    echo "# TYPE flowmonexp_bytes gauge" >> $file
    echo "flowmonexp_bytes $exp_bytes" >> $file
    echo "# HELP flowmonexp_packets Number of packets processed by the exporter" >> $file
    echo "# TYPE flowmonexp_packets gauge" >> $file
    echo "flowmonexp_packets $exp_packets" >> $file
    echo "# HELP flowmonexp_flows_merged Number of flows merged by the exporter" >> $file
    echo "# TYPE flowmonexp_flows_merged gauge" >> $file
    echo "flowmonexp_flows_merged $flows_merged" >> $file
    echo "# HELP flowmonexp_flows_queued Number of flows queued by the exporter" >> $file
    echo "# TYPE flowmonexp_flows_queued gauge" >> $file
    echo "flowmonexp_flows_queued $flows_queued" >> $file
    echo "# HELP flowmonexp_collisions Number of flow cache collisions of exporter" >> $file
    echo "# TYPE flowmonexp_collisions gauge" >> $file
    echo "flowmonexp_collisions $collisions" >> $file

    echo "# HELP int1_packets Number of packets processed by first port" >> $file
    echo "# TYPE int1_packets counter" >> $file
    echo "int1_packets $interfaceStats1" >> $file

    echo "# HELP int1_drops Number of packets dropped by first monitoring port" >> $file
    echo "# TYPE int1_drops counter" >> $file
    echo "int1_drops $interfaceDrops1" >> $file

    echo "# HELP int2_packets Number of packets processed by second monitoring port" >> $file
    echo "# TYPE int2_packets counter" >> $file
    echo "int2_packets $interfaceStats2" >> $file

    echo "# HELP int2_drops Number of packets dropped by second monitoring port" >> $file
    echo "# TYPE int2_drops counter" >> $file
    echo "int2_drops $interfaceDrops2" >> $file
fi

if [ $ads -gt 0 ]; then
    echo "# HELP ads_events Number of events in five minutes" >> $file
    echo "# TYPE ads_events gauge" >> $file
    echo "ads_events $adsEps" >> $file

    echo "# HELP ads_fps Number of flows processed in five minutes" >> $file
    echo "# TYPE ads_fps gauge" >> $file
    echo "ads_fps $streamFps" >> $file
fi
# Only if running on collector or probe
if [ $proxy -eq 0 ]; then
    echo "# HELP live_lifetime Number of days kept in live profile" >> $file
    echo "# TYPE live_lifetime gauge" >> $file
    echo "live_lifetime $tlife" >> $file

    echo "# HELP profiles Number of profiles created on collector" >> $file
    echo "# TYPE profiles gauge" >> $file
    echo "profiles $profilesNumber" >> $file

    echo "# HELP channels Number of channels created on collector" >> $file
    echo "# TYPE channels gauge" >> $file
    echo "channels $channelsNumber" >> $file
fi
