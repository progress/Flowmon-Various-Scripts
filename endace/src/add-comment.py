#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import logging
import logging
import logging.config
import sys, getopt
import configparser
import psycopg2
import datetime

config = configparser.ConfigParser()
config.read('/data/components/endace/etc/endace.ini')

def connect():
    logging.debug('Connecting to the PostgreSQL database...')
    try:
        conn = psycopg2.connect(host="localhost",database="ads", user="ads", password="ADSp4ssw0rd")
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        exit(1)

    logging.debug('...connected.')
    return conn

def close(conn):
    if(conn):
        conn.close()
    logging.debug('PostgreSQL database connection closed.')

def add_comment(conn, id, url):
    sql = "INSERT INTO events.comments(fk_event, fk_user,time,text) VALUES (%s, %s, NOW(), %s)"
    added = 0
    try:
        cur = conn.cursor()
        cur.execute(sql, (id, 1, url))
        conn.commit()
        # get the number of updated rows
        added = cur.rowcount

    except (Exception, psycopg2.Error) as error:
        logging.error(error)

    return added

# Probe hostname
PROBE = config['Endace']['probe']
# Sources to get traffic from
SOURCES = config['Endace']['sources']

logging.config.fileConfig('/data/components/endace/etc/logging.ini')

def main(argv):
    global PROBE
    global SOURCES
    usage = """usage: add-comment.py <options>

Optional:
    --probe        IP / hostname of Endace probe
    --sources      Data sources for the query"""
    try:
        opts, args = getopt.getopt(argv,"p:s:h:",["probe=","sources="])
    except getopt.GetoptError:
        print (usage)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print (usage)
            sys.exit()
        elif opt in ("-p", "--probe"):
            PROBE = arg
        elif opt in ("-s", "--sources"):
            SOURCES = arg

    logging.info('Starting custom script')
    conn = connect()
    # This part is taking care of looping through the stdin until EOF (Ctrl+D)
    for line in sys.stdin:
        event = line.rstrip().split('\t')
        try:
            logging.info('ID {} - timestamp {} - source IP {}'.format(event[0],event[2],event[10]))
            date = datetime.datetime.strptime(event[2], "%Y-%m-%d %H:%M:%S")
            time_stamp = = str(int(datetime.datetime.timestamp(date))*1000)
            url = 'https://{}/vision2/pivotintovision/?datasources={}&title={}&incidenttime={}&tools=conversations_by_ipaddress%2CtrafficOverTime_by_app&ip={}'.format(PROBE,SOURCES,event[0],time_stamp,event[10])
            add_comment(conn, event[0], url)
        except IndexError:
            logging.error('Incorrect number of parametres passed by ADS. {}'.format(event))

    close(conn)
    logging.info('Everything is done')

if __name__ == "__main__":
       main(sys.argv[1:])