# This class is here to work with ADS API

import json
# To disable warning about unverified HTTPS
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class FlowmonADS:
    def __init__(self, app, rest):
        self.rest = rest
        self.app = app

    # Return information about Event reports
    def get_event_reports(self):
        r = requests.get(self.rest._url('/rest/ads/event-reports'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'Events report section is empty on {}.'.format(self.rest.hostname))
            return 0
        else:
            self.app.log.error(
                'Cannot get information about events report: {} - {}'.format(r.status_code, r.content))
            return 0

    # Add event report
    def add_event_report(self, data):
        payload = {'entity': json.dumps(data)}
        headers = self.rest.get_header()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        r = requests.post(self.rest._url('/rest/ads/event-reports'), data=payload,
                          headers=headers, verify=self.rest.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new event reporting HTTP CODE {} - {}'.format(r.status_code, r.content))
            return 0

    # Modify event report
    def change_event_report(self, data):
        payload = {'entity': json.dumps(data)}
        headers = self.rest.get_header()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        r = requests.put(self.rest._url('/rest/ads/event-reports'), data=payload,
                         headers=headers, verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error('Cannot modify event report ID {} HTTP CODE {} - {}'.format(
                data['id'], r.status_code, r.content))
            return 0

    # Delete event report
    def delete_event_report(self, data):
        r = requests.delete(self.rest._url('/rest/ads/event-reports/{}'.format(data)),
                            headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete event report ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0

    # Return information about perspectives
    def get_perspectives(self):
        r = requests.get(self.rest._url('/rest/ads/perspectives'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'Perspectives section is empty on {}.'.format(self.rest.hostname))
            return 0
        else:
            self.app.log.error(
                'Cannot get information about perspectives: {} - {}'.format(r.status_code, r.content))
            return 0

    # Add perspective
    def add_perspective(self, data):
        payload = {'entity': json.dumps(data)}
        headers = self.rest.get_header()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        r = requests.post(self.rest._url('/rest/ads/perspectives'), data=payload,
                          headers=headers, verify=self.rest.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new perspective HTTP CODE {} - {}'.format(r.status_code, r.content))
            return 0

    # Modify perspective
    def change_perspective(self, data):
        payload = {'entity': json.dumps(data)}
        headers = self.rest.get_header()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        r = requests.put(self.rest._url('/rest/ads/perspectives'), data=payload,
                         headers=headers, verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot modify perspective ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0

    # Delete perspective
    def delete_perspective(self, data):
        r = requests.delete(self.rest._url('/rest/ads/perspectives/{}'.format(data)),
                            headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete perspective ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0

    # Return information about data feeds
    def get_data_feeds(self):
        r = requests.get(self.rest._url('/rest/ads/net-flow-sources'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'Data feeds section is empty on {}.'.format(self.rest.hostname))
            return 0
        else:
            self.app.log.error(
                'Cannot get information about data feeds: {} - {}'.format(r.status_code, r.content))
            return 0

    # Add data feed
    def add_data_feed(self, data):
        payload = {'entity': json.dumps(data)}
        headers = self.rest.get_header()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        r = requests.post(self.rest._url('/rest/ads/net-flow-sources'), data=payload,
                          headers=headers, verify=self.rest.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new perspective HTTP CODE {} - {}'.format(r.status_code, r.content))
            return 0

    # Modify data feed
    def change_data_feed(self, data):
        payload = {'entity': json.dumps(data)}
        headers = self.rest.get_header()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        r = requests.put(self.rest._url('/rest/ads/net-flow-sources'), data=payload,
                         headers=headers, verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot modify data feed ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0

    # Delete data feed
    def delete_data_feed(self, data):
        r = requests.delete(self.rest._url('/rest/ads/net-flow-sources/{}'.format(
            data)), headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete data feed ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0

    # Return information about methods
    def get_methods(self):
        r = requests.get(self.rest._url('/rest/ads/methods'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot get information about data feeds: {} - {}'.format(r.status_code, r.content))
            return 0

    # Activate method
    def activate_method(self, data):
        r = requests.put(self.rest._url('/rest/ads/methods/{}/activate'.format(data)),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot activate method {} - {}'.format(r.status_code, r.content))
            return 0

    # Deactivate method
    def deactivate_method(self, data):
        r = requests.delete(self.rest._url('/rest/ads/methods/{}/deactivate'.format(
            data)), headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete data feed ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0

    # Return information about method instance
    def get_instance(self, data):
        r = requests.get(self.rest._url('/rest/ads/method-instances/{}'.format(data)),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot get information about instance: {} - {}'.format(r.status_code, r.content))
            return 0

    # Add instance
    def add_instance(self, data):
        payload = {'entity': json.dumps(data)}
        headers = self.rest.get_header()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        r = requests.post(self.rest._url('/rest/ads/method-instances'), data=payload,
                          headers=headers, verify=self.rest.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new method instance {} - {}'.format(r.status_code, r.content))
            return 0

    # Modify instance
    def change_instance(self, data):
        payload = {'entity': json.dumps(data)}
        headers = self.rest.get_header()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        r = requests.put(self.rest._url('/rest/ads/method-instances'), data=payload,
                         headers=headers, verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot modify instance ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0

    # Delete instanced
    def delete_instance(self, data):
        r = requests.delete(self.rest._url('/rest/ads/method-instances/{}'.format(
            data)), headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete instance ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0

    # Return information about filters
    def get_filters(self):
        r = requests.get(self.rest._url('/rest/ads/filters'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'No filter defined {}.'.format(self.rest.hostname))
            return 0
        else:
            self.app.log.error(
                'Cannot get information about events report: {} - {}'.format(r.status_code, r.content))
            return 0

    # Add filter
    def add_filter(self, data):
        payload = {'entity': json.dumps(data)}
        headers = self.rest.get_header()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        r = requests.post(self.rest._url('/rest/ads/filters'), data=payload,
                          headers=headers, verify=self.rest.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new filter HTTP CODE {} - {}'.format(r.status_code, r.content))
            return 0

    # Modify filter
    def change_filter(self, data):
        payload = {'entity': json.dumps(data)}
        headers = self.rest.get_header()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        r = requests.put(self.rest._url('/rest/ads/filters'), data=payload,
                         headers=headers, verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot modify filter ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0

    # Delete filter
    def delete_filter(self, data):
        r = requests.delete(self.rest._url('/rest/ads/filters/{}'.format(data)),
                            headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete filter ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0

    # Return information about false-positives
    def get_fps(self):
        r = requests.get(self.rest._url('/rest/ads/false-positives'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'No false-positives defined {}.'.format(self.rest.hostname))
            return 0
        else:
            self.app.log.error(
                'Cannot get information about false-positives: {} - {}'.format(r.status_code, r.content))
            return 0

    # Return information about specific false-positive
    def get_fp(self, data):
        r = requests.get(self.rest._url('/rest/ads/false-positives/{}'.format(data)),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot get information about false-positives: {} - {}'.format(r.status_code, r.content))
            return 0

    # Add false-positive
    def add_fp(self, data):
        payload = {'entity': json.dumps(data)}
        headers = self.rest.get_header()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        r = requests.post(self.rest._url('/rest/ads/false-positives'), data=payload,
                          headers=headers, verify=self.rest.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new false-positive HTTP CODE {} - {}'.format(r.status_code, r.content))
            return 0

    # Delete false-positive
    def delete_fp(self, data):
        r = requests.delete(self.rest._url('/rest/ads/false-positives/{}'.format(data)),
                            headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete false-positive ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0

    # Return information about report chapters
    def get_chapters(self):
        r = requests.get(self.rest._url('/rest/ads/pdf-report-chapters'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'No report chapters defined {}.'.format(self.rest.hostname))
            return 0
        else:
            self.app.log.error(
                'Cannot get information about report chapters: {} - {}'.format(r.status_code, r.content))
            return 0

    # Add chapter
    def add_chapter(self, data):
        payload = {'entity': json.dumps(data)}
        headers = self.rest.get_header()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        r = requests.post(self.rest._url('/rest/ads/pdf-report-chapters'), data=payload,
                          headers=headers, verify=self.rest.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new report chapter HTTP CODE {} - {}'.format(r.status_code, r.content))
            return 0

    # Modify chapter
    def change_chapter(self, data):
        payload = {'entity': json.dumps(data)}
        headers = self.rest.get_header()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        r = requests.put(self.rest._url('/rest/ads/pdf-report-chapters'), data=payload,
                         headers=headers, verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error('Cannot modify report chapter ID {} HTTP CODE {} - {}'.format(
                data['id'], r.status_code, r.content))
            return 0

    # Delete chapter
    def delete_chapter(self, data):
        r = requests.delete(self.rest._url('/rest/ads/pdf-report-chapters/{}'.format(
            data)), headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete report chapter ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0
