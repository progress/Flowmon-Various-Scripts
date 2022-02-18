#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
The script can delete multiple False Positive rules from the ADS configuration which have
not been used for a certain time to make it more effective in processing.
=========================================================================================
"""
import logging
from os import stat
from pydoc import cli
import sys, getopt
import json
import time
import requests
# To disable warning about unverified HTTPS
from requests.packages.urllib3.exceptions import InsecureRequestWarning

FORMAT = '%(asctime)s - %(module)s - %(levelname)s : %(message)s'
logging.basicConfig(filename='/tmp/fpcleanup.log', format=FORMAT, level=logging.DEBUG)
client = requests.session()
BASE_URL = 'https://localhost/'

# Connection to the Appliance
def connect(username, password):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    payload = {
        'grant_type' : 'password',
        'client_id' : 'invea-tech',
        'username': username,
        'password': password
    }
    
    client.verify = False
    logging.info('Attemting to connect to Flowmon API at {}'.format(BASE_URL))
    
    url = BASE_URL + 'resources/oauth/token'
    # Login to the flowmon appliance
    login_response = client.post(url, data=payload)
    if login_response.status_code != 200 :
        # Authentication failed
        logging.error('Authentication to {} failed!'.format(BASE_URL))
        exit()

    logging.info('Authenticated successfully to {}!'.format(BASE_URL))
    client.headers['Authorization'] = 'bearer ' + login_response.json()['access_token']

def delete_fp(id):
    url = BASE_URL + 'rest/ads/false-positives/{}'.format(id)
    status = client.delete(url)

    if status.status_code == 204:
        logging.debug('Deleted FP rule {}'.format(id))
        return 1
    else:
        logging.error('Cannot delete false-positive ID {} HTTP CODE {} - {}'.format(id, status.status_code, status.content))
        return 0

def get_fps():
    url = BASE_URL + 'rest/ads/false-positives'
    status = client.get(url)

    if status.status_code == 200:
        logging.debug('Aquired information about all false-positives')
        return json.loads(status.content)
    else:
        logging.error('Cannot get false-positives HTTP CODE {} - {}'.format(status.status_code, status.content))
        return 0

def main(argv):
    empty = False
    usr = 'admin'
    passwd = 'admin'
    before = None
    usage = """usage: fpcleanup.py <options>
    
Mandatory:
    --before YYYY-MM-DD    Date in format YYYY-MM-DD (i.e., 2022-02-18). This is time which would be used
                           as the oldest when the false-positive was used the last time
    
Optional:
    --empty yes            Delete also these not used since creation
    --user <username>      Username used for the authentication to Flowmon appliance
    --pass <password>      Password for the user authentication"""

    
    try:
        opts, args = getopt.getopt(argv,"b:p:u:e:h:",["before=","pass=","user=","empty="])
    except getopt.GetoptError as e:
        print(e)
        print (usage)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print (usage)
            sys.exit()
        elif opt in ("-p", "--pass"):
            passwd = arg
        elif opt in ("-u", "--user"):
            usr = arg
        elif opt in ("-b", "--before"):
            before = arg
        elif opt in ("-e", "--empty"):
            empty = True

    logging.info('Starting false-positive cleanup script')
    if before is None:
        logging.error('before parameter is missing and it is required!')
        exit()
    
    connect(usr,passwd)
    fps = get_fps()
    logging.info('There are {} false-positives'.format(len(fps)))
    print('There are {} false-positives'.format(len(fps)))
    deleted = 0
    kept = 0
    if fps:
        for fp in fps:
            if fp['lastIgnored']:
                if time.strptime(fp['lastIgnored'], "%Y-%m-%d %H:%M:%S") < time.strptime(before, "%Y-%m-%d"):
                    delete_fp(fp['id'])
                    deleted = deleted+1
                else:
                    logging.debug('Keeping false-positive {} - {} - {}'.format(fp['id'], fp['code'], fp['comment']))
                    kept = kept+1
            elif empty:
                delete_fp(fp['id'])
                deleted = deleted+1
            else:
                logging.debug('Keeping false-positive {} - {} - {}'.format(fp['id'], fp['code'], fp['comment']))
                kept = kept+1
    print('Deleted {} rules, kept {} rules'.format(deleted, kept))
    logging.info('The script is completed')

if __name__ == "__main__":
       main(sys.argv[1:])