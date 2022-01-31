# This class is here to initiate the connection to the Flowmon

import json
from core.FlowmonSQL import FlowmonSQL
# To disable warning about unverified HTTPS
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class FlowmonREST:
    # For the start it needs the following arguments
    # string host : Hostname where we want to connect
    # string user : username we are going to use for connection
    # string passw : User password for connection
    def __init__(self, app, host, user, passw):
        self.hostname = host
        self.username = user
        self.password = passw
        self.token = ''
        if app.config.get('REST', 'verify') == "False":
            self.verify = False
        else:
            self.verify = True
        self.app = app
        self.connected = self.connect()

    # helper to build a good URL
    def _url(self, path):
        return "https://" + self.hostname + path

    def get_verify(self):
        return self.verify

    # connection method which will open a connection to API of Flowmon
    # bool verify : Tell if the certificate errors should be ignored
    def connect(self):
        url = '/resources/oauth/token'
        payload = {'grant_type': 'password',
                   'client_id': 'invea-tech',
                   'username': self.username,
                   'password': self.password
                   }
        try:
            r = requests.post(self._url(url), data=payload, verify=self.verify)

            if r.status_code != 200:
                self.app.log.error(
                    'Cannot autheticate to Flowmon {} : {} - {}'.format(self.hostname, r.status_code, r.content))
                return False
            else:
                self.app.log.info(
                    'API User successfuly authenticated to {}'.format(self.hostname))

            self.token = r.json()['access_token']
            return True
        except(Exception, requests.TooManyRedirects) as error:
            self.app.log.error('Too many redirects: {}'.format(error))
            return False
        except(Exception, requests.ConnectionError) as error:
            self.app.log.error('Connection error: {}'.format(error))
            return False
        except(Exception, requests.Timeout) as error:
            self.app.log.error('Timeout: {}'.format(error))
            return False

    # returns authentication token for the header
    def get_header(self):
        return {'Authorization': 'bearer ' + self.token, 'Content-Type': 'application/json'}

    # returns basic information about the collector
    def get_basicinfo(self):
        r = requests.get(self._url('/rest/fcc/device/info'),
                         headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 200:
            return r.content
        else:
            self.app.log.error('Cannot get information about the device {}: {}'.format(
                r.status_code, r.content))
            return 0
    # end def get_basicinfo( self ):

    # returns basic information about the collector
    def get_version(self):
        r = requests.get(self._url('/rest/version'),
                         headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error('Cannot get information about version of the device {}: {}'.format(
                r.status_code, r.content))
            return 0
    # end def get_version( self ):

    # returns basic information about the collector
    def delete_unused_chapters(self):
        sql = FlowmonSQL(self.app)
        ids = sql.get_unused_chapters()
        number = len(ids)
        self.app.log.info('There are {} unused chapters.'.format(number))
        counter = 1
        for id in ids:
            r = requests.delete(self._url(
                '/rest/fmc/chapters/{}'.format(id[0])), headers=self.get_header(), verify=self.get_verify())
            if r.status_code == 204:
                self.app.log.info(
                    'Deleted ID {}: {}/{}'.format(id[0], counter, number))
            else:
                self.app.log.error('Cannot delete chapter {}: {}'.format(
                    r.status_code, r.content))
            counter += 1
    # end def delete_unused_chapters( self ):

    # returs list of roles
    def get_roles(self):
        r = requests.get(self._url('/rest/fcc/roles'),
                         headers=self.get_header(), verify=self.get_verify())

        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'Business hours section is empty on {}.'.format(self.hostname))
            return 0
        else:
            self.app.log.error(
                'Cannot get roles: {} - {}'.format(r.status_code, r.content))
    # end get_roles( self ):

    def add_role(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.post(self._url('/rest/fcc/roles'), data=payload,
                          headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new role HTTP CODE {} - {}'.format(r.status_code, r.content))
            return 0
    # end add_role( self, role ):

    def change_role(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.put(self._url('/rest/fcc/roles'), data=payload,
                         headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot change role ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0
    # end change_role( self, role ):

    def delete_role(self, data):
        r = requests.delete(self._url('/rest/fcc/roles/{}'.format(data)),
                            headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete role ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0
    # end delete_role( self, data ):

    # returs list of roles
    def get_users(self):
        r = requests.get(self._url('/rest/fcc/users'),
                         headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'Business hours section is empty on {}.'.format(self.hostname))
            return 0
        else:
            self.app.log.error(
                'Cannot get users: {} - {}'.format(r.status_code, r.content))
    # end get_users( self ):

    def add_user(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.post(self._url('/rest/fcc/users'), data=payload,
                          headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new user HTTP CODE {} - {}'.format(r.status_code, r.content))
            return 0
    # end add_user( self, role ):

    def change_user(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.put(self._url('/rest/fcc/users'), data=payload,
                         headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot change user ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0
    # end change_user( self, role ):

    def delete_user(self, data):
        r = requests.delete(self._url('/rest/fcc/users/{}'.format(data)),
                            headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete user ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0
    # end delete_user( self, data ):

    # returs list of profiles
    def get_profiles(self):
        r = requests.get(self._url('/rest/fmc/profiles'),
                         headers=self.get_header(), verify=self.get_verify())

        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot get profiles: {} - {}'.format(r.status_code, r.content))
    # end get_profiles( self ):

    def add_profile(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.post(self._url('/rest/fmc/profiles'), data=payload,
                          headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new profile HTTP CODE {} - {}'.format(r.status_code, r.content))
            return 0
    # end add_profile( self, role ):

    def change_profile(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.put(self._url('/rest/fmc/profiles'), data=payload,
                         headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot change profile ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0
    # end change_profile( self, role ):

    def delete_profile(self, data):
        r = requests.delete(self._url('/rest/fmc/profiles/id?id={}'.format(data)),
                            headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete profile ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0
    # end delete_profile( self, data ):

    # returs all business hours
    def get_bh(self):
        r = requests.get(self._url('/rest/fmc/businessHours'),
                         headers=self.get_header(), verify=self.get_verify())

        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'Business hours section is empty on {}.'.format(self.hostname))
            return 0
        else:
            self.app.log.error(
                'Cannot get business hours: {} - {}'.format(r.status_code, r.content))
            return 0
    # end get_bh( self ):

    def add_bh(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.post(self._url('/rest/fmc/businessHours'), data=payload,
                          headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new business hour HTTP CODE {} - {}'.format(r.status_code, r.content))
            return 0
    # end add_bh( self, role ):

    def change_bh(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.put(self._url('/rest/fmc/businessHours'), data=payload,
                         headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error('Cannot change business hour ID {} HTTP CODE {} - {}'.format(
                data['id'], r.status_code, r.content))
            return 0
    # end change_bh( self, role ):

    def delete_bh(self, data):
        r = requests.delete(self._url('/rest/fmc/businessHours/{}'.format(data)),
                            headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete business hour ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0
    # end delete_bh( self, data ):

    # returs all blacklists
    def get_blacklists(self):
        r = requests.get(self._url('/rest/fmc/blacklists'),
                         headers=self.get_header(), verify=self.get_verify())

        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'Blacklists section is empty on {}.'.format(self.hostname))
            return 0
        else:
            self.app.log.error(
                'Cannot get blacklists: {} - {}'.format(r.status_code, r.content))
    # end get_blacklists( self ):

    def add_blacklist(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.post(self._url('/rest/fmc/blacklists'), data=payload,
                          headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new blacklist HTTP CODE {} - {}'.format(r.status_code, r.content))
            return 0
    # end add_blacklist( self, role ):

    def change_blacklist(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.put(self._url('/rest/fmc/blacklists'), data=payload,
                         headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot change blacklist ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0
    # end change_blacklist( self, role ):

    def delete_blacklist(self, data):
        r = requests.delete(self._url('/rest/fmc/blacklists/{}'.format(data)),
                            headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete blacklist ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0
    # end delete_blacklist( self, data ):

    # returs all chapters
    def get_chapters(self):
        r = requests.get(self._url('/rest/fmc/chapters'),
                         headers=self.get_header(), verify=self.get_verify())

        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'Chapter section is empty on {}.'.format(self.hostname))
        else:
            self.app.log.error(
                'Cannot get chapters: {} - {}'.format(r.status_code, r.content))
    # end get_chapters( self ):

    def add_chapter(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.post(self._url('/rest/fmc/chapters'), data=payload,
                          headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new chapter HTTP CODE {} - {}'.format(r.status_code, r.content))
            return 0
    # end add_chapter( self, role ):

    def change_chapter(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.put(self._url('/rest/fmc/chapters'), data=payload,
                         headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot change chapter ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0
    # end change_chapter( self, role ):

    def delete_chapter(self, data):
        r = requests.delete(self._url('/rest/fmc/chapters/{}'.format(data)),
                            headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete chapter ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0
    # end delete_chapter( self, data ):

    # returs all reports
    def get_reports(self):
        r = requests.get(self._url('/rest/fmc/reports'),
                         headers=self.get_header(), verify=self.get_verify())

        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info('No report defined on {}.'.format(self.hostname))
        else:
            self.app.log.error(
                'Cannot get reports: {} - {}'.format(r.status_code, r.content))
    # end get_reports( self ):

    def add_report(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.post(self._url('/rest/fmc/reports'), data=payload,
                          headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new report HTTP CODE {} - {}'.format(r.status_code, r.content))
            return 0
    # end add_report( self, role ):

    def change_report(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.put(self._url('/rest/fmc/reports'), data=payload,
                         headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot change report ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0
    # end change_report( self, role ):

    def delete_report(self, data):
        r = requests.delete(self._url('/rest/fmc/reports/{}'.format(data)),
                            headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete report ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0
    # end delete_report( self, data ):

    # returs all email reports
    def get_emailreports(self):
        r = requests.get(self._url('/rest/fmc/emailReports'),
                         headers=self.get_header(), verify=self.get_verify())

        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'No email report defined on {}.'.format(self.hostname))
        else:
            self.app.log.error(
                'Cannot get email reports: {} - {}'.format(r.status_code, r.content))
    # end get_emailreports( self ):

    def add_emailreport(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.post(self._url('/rest/fmc/emailReports'), data=payload,
                          headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new email report HTTP CODE {} - {}'.format(r.status_code, r.content))
            return 0
    # end add_emailreport( self, role ):

    def change_emailreport(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.put(self._url('/rest/fmc/emailReports'), data=payload,
                         headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error('Cannot change email report ID {} HTTP CODE {} - {}'.format(
                data['id'], r.status_code, r.content))
            return 0
    # end change_emailreport( self, role ):

    def delete_emailreport(self, data):
        r = requests.delete(self._url('/rest/fmc/emailReports/{}'.format(data)),
                            headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete email report ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0
    # end delete_emailreport( self, data ):

    # returs all alerts
    def get_alerts(self):
        r = requests.get(self._url('/rest/fmc/alerts'),
                         headers=self.get_header(), verify=self.get_verify())

        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info('No alerts defined on {}.'.format(self.hostname))
            return False
        else:
            self.app.log.error(
                'Cannot get alerts: {} - {}'.format(r.status_code, r.content))
            return False
    # end get_emailreports( self ):

    def add_alert(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.post(self._url('/rest/fmc/alerts'), data=payload,
                          headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new alert HTTP CODE {} - {}'.format(r.status_code, r.content))
            return 0
    # end add_alert( self, role ):

    def change_alert(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.put(self._url('/rest/fmc/alerts'), data=payload,
                         headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot change alert ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0
    # end change_alert( self, role ):

    def delete_alert(self, data):
        r = requests.delete(self._url('/rest/fmc/alerts/{}'.format(data)),
                            headers=self.get_header(), verify=self.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete alert ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0
    # end delete_alert( self, data ):
