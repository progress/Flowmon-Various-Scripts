#!/home/flowmon/kafka/bin/python3
# -*- coding: utf-8 -*-
"""
This script is to aggregate flow data for streaming to kafka

=========================================================================================
"""

import argparse
from decimal import Rounded
import logging
import subprocess
import shlex
from kafka import KafkaProducer
from kafka.errors import KafkaError
import cbor
import datetime

LOGGING_FORMAT = '%(asctime)s - %(module)s - %(levelname)s : %(message)s'
logging.basicConfig(filename='/home/flowmon/kafka/kafka-stream.log', format=LOGGING_FORMAT, level=logging.DEBUG)

def parse_arguments():
    parser = argparse.ArgumentParser(prog='stream-flow-asn.py')
    parser.add_argument("-i", "--host", action='store', type=str, help="IP address/hostname of the bootstrap server", required=True)
    parser.add_argument("-p", "--port", action='store', type=int, help="Port running boostrap server", required=True, default=9092)
    parser.add_argument("-t", "--topic", action='store', type=str, help="Kafka topic to stream", default='network-metadata')
    arguments = vars(parser.parse_args())
    return arguments

def roundDownDateTime(dt):
    delta_min = dt.minute % 5
    return datetime.datetime(dt.year, dt.month, dt.day,
                             dt.hour, dt.minute - delta_min)

def run_command(command_line):
    arguments = shlex.split(command_line)
    p = subprocess.Popen(arguments, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    std_data = p.communicate()
    output = (p.returncode, std_data[0].decode("utf8"), std_data[1].decode("utf8"))
    return output

def process_records(data):
    records = []
    lines = data.splitlines()
    # Get rid of the headers
    lines.pop(0)
    # Get a statistics and send them to log
    sysstat = lines.pop()
    logging.debug(f"nfdump processing stats: {sysstat}")
    # number of processed flows
    totals = lines.pop()
    logging.debug(totals)
    # time window information we will just drop
    lines.pop()
    # same for summary stats
    lines.pop()
    # so now we have the lines with data only
    for line in lines:
       rows = line.split(',')
       record = {'first_seen': rows[0],
                 'dst_ctr': rows[1].strip(),
                 'duration': rows[2].strip(),
                 'packets': rows[3].strip(),
                 'bytes': rows[4].strip(),
                 'pps': rows[5].strip(),
                 'bps': rows[6].strip(),
                 'flows': rows[7].strip()}
       records.append(record)
    return records

def get_data(timestamp):
    # Get the data from collector
    command = f"/usr/local/bin/nfdump -M /data/nfsen/profiles-data/live/'127-0-0-1_p3000:127-0-0-1_p2055' -r {timestamp} -A 'dstctry' -o 'fmt:%ts,%dcc,%td,%pkt,%byt,%pps,%bps,%fl' -6 --no-scale-number"
    logging.debug(command)
    output = run_command(command)
    if output[0] == 0:
        logging.debug(f"Commmand processed succesfully.")
        return output[1]
    else:
        logging.error(output)

def on_success(metadata):
    logging.info(f"Message produced to topic '{metadata.topic}' at offset {metadata.offset}")

def on_error(e):
    logging.error(f"Error sending message: {e}")

def get_timestamp():
    try:
        file = open('/home/flowmon/kafka/last', 'r')
        datestamp = file.read()
        file.close()
        dateobj = datetime.datetime.strptime(datestamp,"%Y%m%d%H%M")
        dateob_5 = dateobj + datetime.timedelta(minutes=5)
        return dateob_5
    except IOError:
        current = datetime.datetime.now()
        file = open('/home/flowmon/kafka/last', 'w+')
        dateob_5 = current - datetime.timedelta(minutes=5)
        rounded = roundDownDateTime(dateob_5)
        str_time = rounded.strftime("%Y%m%d%H%M")
        file.write(str_time)
        file.close()
        return rounded
def kafka_stream(args, records):
    producer = KafkaProducer(bootstrap_servers = f"{args['host']}:{args['port']}",
                             value_serializer=lambda m: cbor.dumps(m))

    for record in records:
        stream = producer.send(args['topic'],record)
        stream.add_callback(on_success)
        stream.add_errback(on_error)

    producer.flush()
    producer.close()

def main():
    logging.info('------- New run -------')
    args = parse_arguments()
    timestamp = get_timestamp()
    str_time = timestamp.strftime("%Y%m%d%H%M")
    full_path = timestamp.strftime("%Y/%m/%d/") + "nfcapd." + str_time
    logging.debug('Processing {}'.format(full_path))
    data = get_data(full_path)
    records = process_records(data)
    kafka_stream(args, records)

    logging.info('Everything is done')

if __name__ == "__main__":
       main()