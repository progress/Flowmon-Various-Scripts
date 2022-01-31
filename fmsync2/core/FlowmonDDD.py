from core.FlowmonREST import FlowmonREST
import requests
import logging
import json


class FlowmonDDD:
    def __init__(self, app, rest):
        self.rest = rest
        self.app = app

    # Return information about Groups
    def get_groups(self):
        r = requests.get(self.rest._url('/rest/iad/groups/'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            # no groups defined
            self.app.log.info(
                'There are no groups configured on host {}.'.format(self.rest.hostname))
        elif r.status_code == 404:
            # return code 404 if groups do not exists, this way we can detect that v4 of DDD is used
            return 404
        else:
            self.app.log.error(
                'Cannot get information about groups:{} - {}'.format(r.status_code, r.content))
            return 0

    def add_group(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.post(self.rest._url('/rest/iad/groups/'), data=payload,
                          headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new group HTTP CODE {} - {}'.format(r.status_code, r.content))
            return 0

    def change_group(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.put(self.rest._url('/rest/iad/groups/'), data=payload,
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot modify group ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0

    def delete_group(self, data):
        r = requests.delete(self.rest._url('/rest/iad/groups/{}'.format(data)),
                            headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete group ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0

    # Return information about Segment
    # int id ID of segment we want to get
    def get_segment(self, id):
        r = requests.get(self.rest._url('/rest/iad/segments/{}'.format(id)),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot get information about segment {}: {} - {}'.format(id, r.status_code, r.content))

    # Return information about alert configuration of specific segment
    # int id ID of segment
    def get_segment_alert(self, id):
        r = requests.get(self.rest._url('/rest/iad/segments/{}'.format(id)),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            alert = json.loads(r.content)['measures']['alert']
            alert = str(alert)
            if 'None' == alert:
                self.app.log.info('No alerting configured for the segment')
            else:
                alertId = str(json.loads(r.content)['measures']['alert']['id'])

                return self.get_alert(alertId)
        else:
            self.app.log.error(
                'Cannot get information about segment {}: {} - {}'.format(id, r.status_code, r.content))

    # Return alert configuration
    def get_alert(self, id):
        r = requests.get(self.rest._url('/rest/iad/alerts/{}'.format(id)),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot get information about alert {}: {} - {}'.format(id, r.status_code, r.content))
    # end def get_alert( self, id ):

    # Get specific email template
    def get_template(self, id):
        r = requests.get(self.rest._url('/rest/iad/email-templates/{}'.format(id)),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())

        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot get email template {}: {} - {}'.format(id, r.status_code, r.content))
    # end get_template( self, id ):

    # This method returns Segment ID fo specific Attack ID
    #
    def get_attack_segment(self, id):
        r = requests.get(self.rest._url('/rest/iad/attacks/{}'.format(id)),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            segment = json.loads(r.content)['segment']['id']
            return str(segment)
        else:
            self.app.log.error(
                'Cannot get information about attack {}: {} - {}'.format(id, r.status_code, r.content))
    # end def get_attack_segment( self, id ):

    # This method returns Segment ID fo specific Attack ID
    #
    def get_attack(self, id):
        r = requests.get(self.rest._url('/rest/iad/attacks/{}'.format(id)),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot get information about attack {}:  {} - {}'.format(id, r.status_code, r.content))
    # end def get_attack_segment( self, id ):

    def get_routers(self):
        r = requests.get(self.rest._url('/rest/iad/routers/'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'Routers section is empty on {}.'.format(self.rest.hostname))
            return 0
        else:
            self.app.log.error(
                'Cannot get information about routers {} - {}'.format(r.status_code, r.content))
            return 0
    # end def get_routers( self ):

    def get_alerts(self):
        r = requests.get(self.rest._url('/rest/iad/alerts/'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'Alerts section is empty on {}.'.format(self.rest.hostname))
            return False
        else:
            self.app.log.error(
                'Cannot get information about alerts {} - {}'.format(r.status_code, r.content))
            return False
    # end def get_alerts( self ):

    def get_scrubbing(self):
        r = requests.get(self.rest._url('/rest/iad/scrubbing-centers/'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'Scrubbing section is empty on {}.'.format(self.rest.hostname))
            return 0
        else:
            self.app.log.error(
                'Cannot get information about scrubbing-centers {} - {}'.format(r.status_code, r.content))
            return 0
    # end def get_scrubbings( self ):

    def get_scrubbing_parameters(self):
        r = requests.get(self.rest._url('/rest/iad/scrubbing-center-parameters/'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot get information about scrubbing-center parameters {} - {}'.format(r.status_code, r.content))
    # end def get_scrubbings_parameters( self ):

    def get_report_chapters(self):
        r = requests.get(self.rest._url('/rest/iad/report-chapter/'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'Report chapters section is empty on {}.'.format(self.rest.hostname))
            return 0
        else:
            self.app.log.error(
                'Cannot get information about report-chapters HTTP CODE {} - {}'.format(r.status_code, r.content))
    # end def get_report_chapters( self ):

    def get_email_templates(self):
        r = requests.get(self.rest._url('/rest/iad/email-templates/'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'Email templates section is empty on {}.'.format(self.rest.hostname))
            return 0
        else:
            self.app.log.error(
                'Cannot get information about email-templates HTTP CODE {} - {}'.format(r.status_code, r.content))
    # end def get_email_templates( self ):

    def get_rules(self):
        r = requests.get(self.rest._url('/rest/iad/rules/'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'Rules section is empty on {}.'.format(self.rest.hostname))
            return 0
        else:
            self.app.log.error(
                'Cannot get information about rules HTTP CODE {} - {}'.format(r.status_code, r.content))
    # end def get_rules( self ):

    def get_segments(self):
        r = requests.get(self.rest._url('/rest/iad/segments/'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'Segments section is empty on {}.'.format(self.rest.hostname))
            return 0
        else:
            self.app.log.error(
                'Cannot get information about segments HTTP CODE {} - {}'.format(r.status_code, r.content))
    # end def get_segments( self ):

    def add_router(self, router):
        payload = {'entity': router}
        payload = json.dumps(payload)
        r = requests.post(self.rest._url('/rest/iad/routers/'), data=payload,
                          headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new router ID {} HTTP CODE {} - {}'.format(router['id'], r.status_code, r.content))
            return 0

    def change_router(self, router):
        payload = {'entity': router}
        payload = json.dumps(payload)
        r = requests.put(self.rest._url('/rest/iad/routers/'), data=payload,
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot modify router ID {} HTTP CODE {} - {}'.format(router['id'], r.status_code, r.content))
            return 0

    def delete_router(self, router):
        r = requests.delete(self.rest._url('/rest/iad/routers/{}'.format(router)),
                            headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete router ID {} HTTP CODE {} - {}'.format(router, r.status_code, r.content))
            return 0

    def add_scrubbing(self, scrubbing):
        payload = {'entity': scrubbing}
        payload = json.dumps(payload)
        r = requests.post(self.rest._url('/rest/iad/scrubbing-centers/'), data=payload,
                          headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error('Cannot add new scrubbing-center ID {} HTTP CODE {} - {}'.format(
                scrubbing['id'], r.status_code, r.content))
            return 0

    def change_scrubbing(self, scrubbing):
        payload = {'entity': scrubbing}
        payload = json.dumps(payload)
        r = requests.put(self.rest._url('/rest/iad/scrubbing-centers/'), data=payload,
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error('Cannot modify scrubbing-center ID {} HTTP CODE {} - {}'.format(
                scrubbing['id'], r.status_code, r.content))
            return 0

    def delete_scrubbing(self, scrubbing):
        r = requests.delete(self.rest._url('/rest/iad/scrubbing-centers/{}'.format(
            scrubbing)), headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete scrubbing-center ID {} HTTP CODE {} - {}'.format(scrubbing, r.status_code, r.content))
            return 0

    def add_alert(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.post(self.rest._url('/rest/iad/alerts/'), data=payload,
                          headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new alert ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0

    def change_alert(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.put(self.rest._url('/rest/iad/alerts/'), data=payload,
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot modify alert ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0

    def delete_alert(self, data):
        r = requests.delete(self.rest._url('/rest/iad/alerts/{}'.format(data)),
                            headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete alert ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0

    def change_scrubbing_parametres(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.put(self.rest._url('/rest/iad/scrubbing-center-parameters'),
                         data=payload, headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot modify alert HTTP CODE {} - {}'.format(r.status_code, r.content))
            return 0

    def add_chapter(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.post(self.rest._url('/rest/iad/report-chapter/'), data=payload,
                          headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new chapter ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0

    def change_chapter(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.put(self.rest._url('/rest/iad/report-chapter/'), data=payload,
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot modify chapter ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0

    def delete_chapter(self, data):
        r = requests.delete(self.rest._url('/rest/iad/report-chapter/{}'.format(data)),
                            headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete chapter ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0

    def add_template(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.post(self.rest._url('/rest/iad/email-templates/'), data=payload,
                          headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error('Cannot add new email template ID {} HTTP CODE {} - {}'.format(
                data['id'], r.status_code, r.content))
            return 0

    def change_template(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.put(self.rest._url('/rest/iad/email-templates/'), data=payload,
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error('Cannot modify email template ID {} HTTP CODE {} - {}'.format(
                data['id'], r.status_code, r.content))
            return 0

    def delete_template(self, data):
        r = requests.delete(self.rest._url('/rest/iad/email-templates/{}'.format(data)),
                            headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete email template ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0

    def add_rule(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.post(self.rest._url('/rest/iad/rules/'), data=payload,
                          headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new rule {} HTTP CODE {} - {}'.format(data['name'], r.status_code, r.content))
            return 0

    def change_rule(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.put(self.rest._url('/rest/iad/rules/'), data=payload,
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot modify rule ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0

    def delete_rule(self, data):
        r = requests.delete(self.rest._url('/rest/iad/rules/{}'.format(data)),
                            headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete rule ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0

    def add_segment(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.post(self.rest._url('/rest/iad/segments/'), data=payload,
                          headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new segment ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0

    def change_segment(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.put(self.rest._url('/rest/iad/segments/'), data=payload,
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot modify segment ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0

    def delete_segment(self, data):
        r = requests.delete(self.rest._url('/rest/iad/segments/{}'.format(data)),
                            headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete segment ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0

    # Return information about Whitelists
    def get_whitelists(self):
        r = requests.get(self.rest._url('/rest/iad/whitelists'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'DDD: No whitelistst configured on {}.'.format(self.rest.hostname))
        else:
            self.app.log.error(
                'DDD: Cannot get information about whitelists : {} - {}'.format(r.status_code, r.content))

    def add_whitelist(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.post(self.rest._url('/rest/iad/whitelists/'), data=payload,
                          headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new whitelist name {} HTTP CODE {} - {}'.format(data['name'], r.status_code, r.content))
            return 0

    def change_whitelist(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.put(self.rest._url('/rest/iad/whitelists/'), data=payload,
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot modify whitelist ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0

    def delete_whitelist(self, data):
        r = requests.delete(self.rest._url('/rest/iad/whitelists/{}'.format(data)),
                            headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete whitelist ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0

    # Return information about traffic types
    def get_traffictypes(self):
        r = requests.get(self.rest._url('/rest/iad/whitelists/traffic-types'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'DDD: Cannot get information about traffic types: {} - {}'.format(r.status_code, r.content))

    # Return information about Custom baselines
    def get_custombaselines(self):
        r = requests.get(self.rest._url('/rest/iad/custom-baselines'),
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        elif r.status_code == 204:
            self.app.log.info(
                'DDD: There are no custom baselines on {}.'.format(self.rest.hostname))
        else:
            self.app.log.error(
                'DDD: Cannot get information about custom baselines : {} - {}'.format(r.status_code, r.content))

    def add_custombaseline(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.post(self.rest._url('/rest/iad/custom-baselines/'), data=payload,
                          headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 201:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot add new custom baseline ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0

    def change_custombaseline(self, data):
        payload = {'entity': data}
        payload = json.dumps(payload)
        r = requests.put(self.rest._url('/rest/iad/custom-baselines/'), data=payload,
                         headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 200:
            return json.loads(r.content)
        else:
            self.app.log.error(
                'Cannot modify custom baseline ID {} HTTP CODE {} - {}'.format(data['id'], r.status_code, r.content))
            return 0

    def delete_custombaseline(self, data):
        r = requests.delete(self.rest._url('/rest/iad/custom-baselines/{}'.format(data)),
                            headers=self.rest.get_header(), verify=self.rest.get_verify())
        if r.status_code == 204:
            return 1
        else:
            self.app.log.error(
                'Cannot delete custom baseline ID {} HTTP CODE {} - {}'.format(data, r.status_code, r.content))
            return 0

