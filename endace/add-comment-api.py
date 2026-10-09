#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
ADS custom script which adds Endace Pivot-to-Vision link as a comment to ADS event.
Uses the Flowmon ADS REST API (ADS 13.1+) endpoint /rest/ads/v1/event/add-comment
instead of writing directly into the database.
=========================================================================================
"""
import sys, getopt
import datetime
import ipaddress
import logging
import logging.handlers
from urllib.parse import urlencode
import requests
# To disable warning about unverified HTTPS
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# ---------------------------------------------------------------------------------------
# Configuration (can be overridden by script parameters in ADS)
# ---------------------------------------------------------------------------------------
# IP / hostname of Endace probe
PROBE = 'pp9-1.lab.endace.com'
# Data sources for the Endace query
SOURCES = 'target:all'
# Flowmon appliance REST API connection (user needs permission to comment ADS events)
FLOWMON_HOST = 'localhost'
FLOWMON_USER = 'admin'
FLOWMON_PASS = 'admin'
# Verify HTTPS certificate of the Flowmon appliance: True, False or path to a CA bundle.
# Keep certificate verification enabled whenever FLOWMON_HOST is not localhost.
VERIFY_SSL = False
# Log file (directory is writable by ADS scripts)
LOG_FILE = '/data/components/apps/log/endace-add-comment.log'
# Timeout in seconds for REST API requests
TIMEOUT = 30
# ---------------------------------------------------------------------------------------

FORMAT = '%(asctime)s - %(module)s - %(levelname)s : %(lineno)d - %(message)s'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=4)
handler.setFormatter(logging.Formatter(FORMAT))
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)


class FlowmonAPI:
    def __init__(self, host, username, password, verify=False):
        self.base_url = 'https://{}'.format(host)
        self.username = username
        self.password = password
        self.client = requests.session()
        self.client.verify = verify
        if not verify:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def connect(self):
        logging.debug('Authenticating to Flowmon REST API at {}'.format(self.base_url))
        payload = {
            'grant_type': 'password',
            'client_id': 'invea-tech',
            'username': self.username,
            'password': self.password
        }
        try:
            r = self.client.post(self.base_url + '/resources/oauth/token', data=payload,
                                 timeout=TIMEOUT)
        except requests.exceptions.RequestException as error:
            logging.error('Cannot connect to {}: {}'.format(self.base_url, error))
            return False
        if r.status_code != 200:
            logging.error('Authentication to {} failed! HTTP CODE {}'.format(
                self.base_url, r.status_code))
            return False
        try:
            self.client.headers['Authorization'] = 'bearer ' + r.json()['access_token']
        except (ValueError, KeyError):
            logging.error('Unexpected authentication response from {}'.format(self.base_url))
            return False
        logging.debug('Authenticated successfully.')
        return True

    def add_comment(self, event_id, comment, retry=True):
        url = self.base_url + '/rest/ads/v1/event/add-comment'
        try:
            r = self.client.post(url, params={'id': event_id, 'comment': comment},
                                 headers={'accept': 'application/json'}, timeout=TIMEOUT)
        except requests.exceptions.RequestException as error:
            logging.error('Cannot add comment to event {}: {}'.format(event_id, error))
            return False
        # Token could expire during long run, re-authenticate once
        if r.status_code == 401 and retry and self.connect():
            return self.add_comment(event_id, comment, retry=False)
        if r.status_code not in (200, 201, 204):
            logging.error('Cannot add comment to event {} HTTP CODE {} - {}'.format(
                event_id, r.status_code, r.content))
            return False
        logging.debug('Comment added to event {}'.format(event_id))
        return True


def main(argv):
    probe = PROBE
    sources = SOURCES
    host = FLOWMON_HOST
    user = FLOWMON_USER
    passwd = FLOWMON_PASS
    usage = """usage: add-comment-api.py <options>

Optional:
    --probe <host>     IP / hostname of Endace probe
    --sources <src>    Data sources for the query
    --host <host>      Flowmon appliance with ADS (default localhost)
    --user <username>  Username used for the authentication to Flowmon appliance
    --pass <password>  Password for the user authentication"""
    try:
        opts, args = getopt.getopt(argv, "p:s:H:u:P:h",
                                   ["probe=", "sources=", "host=", "user=", "pass=", "help"])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(usage)
            sys.exit()
        elif opt in ("-p", "--probe"):
            probe = arg
        elif opt in ("-s", "--sources"):
            sources = arg
        elif opt in ("-H", "--host"):
            host = arg
        elif opt in ("-u", "--user"):
            user = arg
        elif opt in ("-P", "--pass"):
            passwd = arg

    logging.info('Starting custom script')
    api = FlowmonAPI(host, user, passwd, VERIFY_SSL)
    if not api.connect():
        sys.exit(1)

    # This part is taking care of looping through the stdin until EOF (Ctrl+D)
    added = 0
    for line in sys.stdin:
        event = line.rstrip().split('\t')
        try:
            # Validate fields so nothing unexpected gets into the comment or the log
            event_id = str(int(event[0]))
            date = datetime.datetime.strptime(event[2], "%Y-%m-%d %H:%M:%S")
            source_ip = str(ipaddress.ip_address(event[10]))
            logging.info('ID {} - timestamp {} - source IP {}'.format(event_id, date, source_ip))
            time_stamp = str(int(datetime.datetime.timestamp(date)) * 1000)
            query = urlencode({
                'datasources': sources,
                'title': event_id,
                'incidenttime': time_stamp,
                'tools': 'conversations_by_ipaddress,trafficOverTime_by_app',
                'ip': source_ip
            })
            url = 'https://{}/vision2/pivotintovision/?{}'.format(probe, query)
            if api.add_comment(event_id, url):
                added += 1
        except IndexError:
            logging.error('Incorrect number of parameters passed by ADS: {!r}'.format(line[:200]))
        except ValueError as error:
            logging.error('Cannot parse event {!r}: {}'.format(line[:200], error))

    logging.info('Everything is done, {} comment(s) added'.format(added))


if __name__ == "__main__":
    main(sys.argv[1:])
