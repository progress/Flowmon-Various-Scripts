import json
from core.Persistent import Persistent
import sys
import copy
import operator


class JsonFunc:
    def __init__(self, app, db):
        self.app = app
        self.db = db

    # Function to compare outputs
    def compare(self, master, slave, to_compare, what, first):
        if not slave:
            self.app.log.info('Slave configuration part is empty')
            return 0
        else:
            res = {'missing': [], 'updated': [], 'deleted': []}
            if master == slave:
                self.app.log.info('Configurations are equal')
                if first:
                    for item in master:
                        if what == 'alert':
                            alert = (item['id'], item['id'], item['sendSyslog'],
                            item['sendSnmp'], item['sendEmail'], item['runScript'])
                            self.db.create_alert(alert)
                        elif what == 'fmc_email':
                            email = (item['id'], item['id'], item['active'])
                            self.db.create_fmc_email(email)
                        elif what == 'event_report':
                            email = (item['id'], item['id'], item['active'])
                            self.db.create_event_report(email)
                        else:
                            getattr(self.db, 'create_%s' %
                                what)(item['id'], item['id'])
                # and we are done
                return 1
            else:
                change = 0
                self.app.log.debug('Configurations have some differences')
                extra = copy.deepcopy(slave)
                for item in master:
                    if item not in slave:
                        exists = 1
                        for masti in slave:
                            if item[to_compare] == masti[to_compare]: 
                                #print("Master: {} ---".format(item))
                                #print("Slave: {} ---".format(masti))
                                self.app.log.debug(
                                    'Item exists with slave ID {} - master ID {}'.format(masti['id'], item['id']))
                                exists = 0
                                extra.remove(masti)
                                sid = masti['id']
                                iid = item['id']
                                if first:
                                    if what == 'alert':
                                        alert = (
                                            iid, sid, item['sendSyslog'], item['sendSnmp'], item['sendEmail'], item['runScript'])
                                        self.db.create_alert(alert)
                                    elif what == 'fmc_email':
                                        email = (iid, sid, item['active'])
                                        self.db.create_fmc_email(email)
                                    elif what == 'fmc_alert':
                                        alert = (iid, sid, int(item['definition']['reactions']['syslog']['enabled']), int(item['definition']['reactions']['snmp']['enabled']), int(
                                            item['definition']['reactions']['email']['enabled']), int(item['definition']['reactions']['script']['enabled']))
                                        self.db.create_fmc_alert(alert)
                                    elif what == 'event_report':
                                        self.db.create_event_report(iid, sid, item['active'])
                                    else:
                                        getattr(self.db, 'create_%s' %
                                                what)(iid, sid)
                                del masti['id']
                                del item['id']
                                if what == 'segment':
                                    del masti['flowspecAction']['id']
                                    del item['flowspecAction']['id']
                                    del masti['rule']['id']
                                    del item['rule']['id']
                                    del masti['bandwidthDay']
                                    del item['bandwidthDay']
                                    del masti['bandwidth']
                                    del item['bandwidth']
                                    del masti['trafficSeen']
                                    del item['trafficSeen']
                                    # for v4 only
                                    if 'profileName' in masti:
                                        del masti['profileName']
                                        del item['profileName']
                                        # also verify profiles and channels
                                        if self.db.select_profile(item['parentProfile']['profile']) is not None:
                                            if masti['parentProfile']['profile'] == self.db.select_profile(item['parentProfile']['profile'])[0]:
                                                item['parentProfile']['profile'] = masti['parentProfile']['profile']
                                                if item['parentProfile']['channels'] is not "*":
                                                    difch = 0
                                                    for channel in item['parentProfile']['channels']:
                                                        if self.db.select_channel(channel) is not None:
                                                            if self.db.select_channel(channel)[0] not in masti['parentProfile']['channels']:
                                                                difch = 1
                                                    if not difch:
                                                        item['parentProfile']['channels'] = masti['parentProfile']['channels']
                                    rrkeep = 0
                                    # remove alerts ID
                                    if 'alert' in item['measures'] and item['measures']['alert']:
                                        del item['measures']['alert']['id']
                                    if 'alert' in masti['measures'] and masti['measures']['alert']:
                                        del masti['measures']['alert']['id']
                                    # from reroute we need to remove id and routerId
                                    if 'reroute' in item['measures'] and item['measures']['reroute']:
                                        rrkeep = item['measures']['reroute']
                                        rrma = []
                                        for rrmast in item['measures']['reroute']:
                                            del rrmast['id']
                                            del rrmast['routerId']
                                            del rrmast['segmentId']
                                            rrma.append(rrmast)
                                        rrma = sorted(rrma, key=operator.itemgetter('routerName'))
                                        item['measures']['reroute'] = rrma

                                    if 'reroute' in masti['measures'] and masti['measures']['reroute']:
                                        rrsl = []
                                        for rrslave in masti['measures']['reroute']:
                                            del rrslave['id']
                                            del rrslave['routerId']
                                            del rrslave['segmentId']
                                            rrsl.append(rrslave)
                                        rrsl = sorted(rrsl, key=operator.itemgetter('routerName'))
                                        masti['measures']['reroute'] = rrsl
                                    if 'whitelists' in item:
                                        del item['whitelists']
                                    if 'whitelists' in masti:
                                        del masti['whitelists']
                                # before comparing profiles we remove some keys
                                elif what == 'profile':
                                    del masti['start']
                                    del item['start']
                                    del masti['end']
                                    del item['end']
                                    del masti['parent']
                                    parent = item['parent']
                                    del item['parent']
                                    chkeep = copy.deepcopy(item['channels'])
                                    chma = []
                                    chsl = []
                                    if first:
                                        # add missing channels to DB
                                        for channel in item['channels']:
                                            for orig in masti['channels']:
                                                if orig['name'] == channel['name']:
                                                    self.db.create_channel(
                                                        channel['id'], orig['id'])
                                                    break
                                    for rrmast in item['channels']:
                                        del rrmast['id']
                                        chma.append(rrmast)
                                    for rrslave in masti['channels']:
                                        del rrslave['id']
                                        chsl.append(rrslave)
                                    item['channels'] = chma
                                    masti['channels'] = chsl
                                elif what == 'rule':
                                    if 'subRules' in item:
                                        for sub_rule in item['subRules']:
                                            del sub_rule['id']
                                            del sub_rule['ruleId']
                                            for option in sub_rule['options']:
                                                del option['id']
                                        for sub_rule in masti['subRules']:
                                            del sub_rule['id']
                                            del sub_rule['ruleId']
                                            for option in sub_rule['options']:
                                                del option['id']
                                elif what == 'whitelist':
                                    if item['networks']:
                                        for network in item['networks']:
                                            del network['id']
                                    if masti['networks']:
                                        for network in masti['networks']:
                                            del network['id']
                                    if item['asns']:
                                        for network in item['asns']:
                                            del network['id']
                                    if masti['asns']:
                                        for network in masti['asns']:
                                            del network['id']
                                    if item['whitelistedTrafficTypes']:
                                        for types in item['whitelistedTrafficTypes']:
                                            del types['id']
                                    if masti['whitelistedTrafficTypes']:
                                        for types in masti['whitelistedTrafficTypes']:
                                            del types['id']
                                        
                                if item != masti:
                                    #print("Master: {} ---".format(item))
                                    #print("Slave: {} ---".format(masti))
                                    self.app.log.debug('Differences: {}'.format(set(item) ^ set(masti)))
                                    item['id'] = sid
                                    if what == 'segment':
                                        if rrkeep:
                                            item['measures']['reroute'] = rrkeep
                                    elif what == 'profile':
                                        if chkeep:
                                            item['channels'] = chkeep
                                            item['parent'] = parent
                                    self.app.log.debug(
                                        'Item changed with slave ID {} - master ID {}'.format(sid, iid))
                                    res['updated'].append(item)
                                    change = 1
                                # we found a match
                                break
                        if exists:
                            res['missing'].append(item)
                            change = 1

                    else:
                        if first:
                            if what == 'alert':
                                alert = (item['id'], item['id'], item['sendSyslog'],
                                         item['sendSnmp'], item['sendEmail'], item['runScript'])
                                self.db.create_alert(alert)
                            elif what == 'fmc_email':
                                email = (item['id'], item['id'], item['active'])
                                self.db.create_fmc_email(email)
                            elif what == 'event_report':
                                email = (item['id'], item['id'], item['active'])
                                self.db.create_event_report(email)
                            else:
                                getattr(self.db, 'create_%s' %
                                        what)(item['id'], item['id'])
                        self.app.log.debug('Item exists {}'.format(item['id']))
                        extra.remove(item)
                self.app.log.debug(
                    'There are {} extra items on slave'.format(len(extra)))
                self.app.log.debug(
                    'There are {} missing items on slave'.format(len(res['missing'])))
                self.app.log.debug(
                    'There are {} updated items on slave'.format(len(res['updated'])))
                res['deleted'] = extra
                if len(extra) > 0:
                    change = 1

                if change:
                    return res
                else:
                    return 1