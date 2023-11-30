# Flow data to Kafka streaming

This script is implementing flow data aggregation and streaming of the
results to Kafka stream in CBOR format. It can be easily changed to use
a different format or sent different data. Consider this one as an
example of what is possible and modify it to your needs.

It has been tested with Flowmon system version 12.3.

## Prerequisites

To run it you would need to create a Python virtual environment on your
Flowmon appliance and add necessary libraries which aren’t present on
Flowmon system. This can be achieved by running the following commands:

python3 -m venv kafka

The kafka is a name of the virtual environment. If you use a different
name, you will need to change that in the script as well. The following
is changing directory, and you need to use name of virtual environment
used above. The script then needs to be placed in this folder.

    cd kafka

source bin/activate

pip3 install kafka-python

pip3 install cbor

## Using the script

The script is made to run every five minutes and you can add it to
Flowmon user crontab by editing it with command “crontab -e”. It’s
keeping its last timestamp in a file called last and if this one doesn’t
exist it is created.

When you need to test the script multiple times you would need to delete
this file as it would round the current time to previous 5-minute
interval to run analysis by nfdump console command.

The command to get the aggregation is present in function get\_data.

command = f"/usr/local/bin/nfdump -M
/data/nfsen/profiles-data/live/'127-0-0-1\_p3000:127-0-0-1\_p2055' -r
{timestamp} -A 'dstctry' -o 'fmt:%ts,%dcc,%td,%pkt,%byt,%pps,%bps,%fl'
-6 --no-scale-number"

The result in the SSH command line when tunning this command could look
like following.

Date first seen Dst Ctry Duration Packets Bytes pps bps Flows

2023-11-30 11:29:22.585, 203, 302.210, 760, 58348, 2, 1544, 196

2023-11-30 11:29:39.261, 826, 271.966, 55, 4541, 0, 133, 15

2023-11-30 11:30:08.502, 372, 227.322, 189, 81984, 0, 2885, 13

2023-11-30 11:30:54.374, 250, 150.388, 351, 195125, 2, 10379, 22

2023-11-30 11:27:04.546, 840, 468.700, 4592, 1172714, 9, 20016, 1486

2023-11-30 11:30:06.511, 276, 200.593, 84, 10942, 0, 436, 5

2023-11-30 11:32:00.974, 100, 0.000, 1, 76, 0, 0, 1

2023-11-30 11:25:03.508, 0, 594.975, 829590,893719438,
1394,12016900,14558

2023-11-30 11:29:44.087, 528, 297.434, 676, 204732, 2, 5506, 42

Summary: total flows: 16338, total bytes: 895447900, total packets:
836298, avg bps: 12040141, avg pps: 1405, avg bpp: 1070

Time window: 2023-11-30 11:25:03 - 2023-11-30 11:35:00

Total flows processed: 16338, Blocks skipped: 0, Bytes read: 5883516

Sys: 0.028s flows/second: 569427.0 Wall: 0.010s flows/second: 1603966.2

The easiest way to get the command for aggregation is to run the query
in the Monitoring Center Analysis where you get the results you are
after. Do not forget to select all fields you want to use for
aggregation, filter the data (if needed), select proper output format
and limit on the number of results which are interesting for you. Also
select the right profile and channels where you want to get the data
from.

![A screenshot of a computer Description automatically
generated](media/image1.png)

Once you click on the black terminal window icon it will give the
statistics command. This one would look like the above example so you
can replace this command between quotas. Just change -R to -r
{timestamp}” as it’s in the example so this can change the timestamp of
analyzed data with each run.

When you modify the command, you would need to modify the function
process\_records as the record would have a different format based on
the output you have selected.

The script supports three arguments.

\-i HOST, --host HOST IP address/hostname of the bootstrap server

\-p PORT, --port PORT Port of the running boostrap server

\-t TOPIC, --topic TOPIC Kafka topic to stream

There is a log file located in the script folder (by default
kafka/kafka-stream.log) which can help you with troubleshooting. It does
require connection from external IP to bootstrap Kafka server configured
so it can connect and send data for the specified topic.
