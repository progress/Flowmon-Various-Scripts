- **perfmon.sh** - the scripts take additional metrics from Flowmon Collectors and 100G Probe with Netcope card (older type)
- **perfmon-dpdk.sh** - provides the same output as above but for 100G Probe with Mellanox card (latest)
- **perfmon-node_exporter.sh** - provides the same metrics just in node-exporter text file format. These metrics are explained at https://www.flowmon.com/en/blog/how-to-monitor-your-flowmon-appliances
Tor run it as a docker you can use 
```
sudo docker run -d \
--net="host" \
--pid="host" \
-v "/:/host:ro,rslave" \
-v "/home/flowmon/perfmon/:/var/lib/node_exporter/textfile_collector:ro,rslave" \
quay.io/prometheus/node-exporter:latest \
--path.rootfs=/host \
--collector.textfile.directory=/var/lib/node_exporter/textfile_collector
```
They have to be run by cron in regular intervals. As it is provided it expects to be run every 5 minutes.
- **tora.lab.brn.flowmon.com_2020-06-24_16-43-53.csv** is an example output CSV file.
