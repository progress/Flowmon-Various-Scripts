
from core.JsonFunc import JsonFunc
from core.Persistent import Persistent
from core.controll.ControllFMC import ControllFMC
from core.controll.ControllDDD import ControllDDD
from core.controll.ControllADS import ControllADS
from core.FlowmonREST import FlowmonREST
from core.FlowmonDDD import FlowmonDDD
from core.FlowmonADS import FlowmonADS
import json


class main:
    def __init__(self, app):
        self.app = app
        self.first = False
        self.master = None
        self.slave = None
        self.dddMaster = None
        self.dddSlave = None
        self.func = None
        self.db = None

    def sync(self, first=False):
        # check if we are not a master 
        if self.get_state():
            # We are master so no sync to be done
            return True

        self.master = FlowmonREST(self.app, self.app.config.get(
            'REST', 'remote'), self.app.config.get('REST', 'user'), self.app.config.get('REST', 'pass'))
        if self.master.connected is False:
            return False
        self.slave = FlowmonREST(self.app, self.app.config.get('REST', 'local'), self.app.config.get(
            'REST', 'luser'), self.app.config.get('REST', 'lpass'))
        if self.slave.connected is False:
            return False
        self.db = Persistent(self.app)
        self.func = JsonFunc(self.app, self.db)
        self.first = first
        if self.app.config.get('sync', 'fmc') == 'yes':
            # Do FMC
            self.app.log.info('Syncing FMC portion...')
            fmc_ctrl = ControllFMC(self.app, self.master, self.slave, self.func, self.db, self.first)
            fmc_ctrl.sync()
            self.app.log.info('FMC portion done...')
        if self.app.config.get('sync', 'ads') == 'yes':
            # Do ADS
            self.app.log.info('Syncing ADS portion...')
            ads_ctrl = ControllADS(self.app, self.master, self.slave, self.func, self.db, self.first)
            ads_ctrl.sync()
            self.app.log.info('ADS portion done...')
        if self.app.config.get('sync', 'ddd') == 'yes':
            # Do DDD
            self.app.log.info('Syncing DDD portion...')
            ddd_ctrl = ControllDDD(self.app, self.master, self.slave, self.func, self.db, self.first)
            ddd_ctrl.sync()
            self.app.log.info('DDD portion done...')
        self.db.close_con()
        return True
    # end def sync( self, first=False ):

    def set_state(self, state):
        self.slave = FlowmonREST(self.app, self.app.config.get('REST', 'local'), self.app.config.get(
            'REST', 'luser'), self.app.config.get('REST', 'lpass'))
        self.master = FlowmonREST(self.app, self.app.config.get(
            'REST', 'remote'), self.app.config.get('REST', 'user'), self.app.config.get('REST', 'pass'))
        self.app.log.info('Connection to master {}'.format(self.master.connected))
        self.db = Persistent(self.app)
        self.db.update_state(state)
        self.app.log.info('Mode changed to {}'.format(state))
        self.switch_alerts(state)
        self.db.close_con()

    def init(self):
        self.db = Persistent(self.app)
        self.db.db_init()
        self.db.close_con()

    def live_check(self):
        self.master = FlowmonREST(self.app, self.app.config.get(
            'REST', 'remote'), self.app.config.get('REST', 'user'), self.app.config.get('REST', 'pass'))
        if self.master.connected:
            self.app.log.debug('Master {} is alive'.format(
                self.app.config.get('REST', 'remote')))
            return True
        else:
            self.app.log.debug('Master {} is dead'.format(
                self.app.config.get('REST', 'remote')))
            return False

    def get_state(self):
        self.db = Persistent(self.app)
        state = 'slave' if self.db.select_state()[0] else 'master'
        self.app.log.info('Current state is {}'.format(state))
        # Return True if Master
        return False if self.db.select_state()[0] else True

    # here we switch between slave and master function
    # enable or disable alerting based on original master setup
    def switch_alerts(self, state):
        if self.app.config.get('sync', 'fmc') == 'yes':
            # Do FMC
            self.switch_fmc(state)
        if self.app.config.get('sync', 'ads') == 'yes':
            # Do ADS
            self.switch_ads(state)
        if self.app.config.get('sync', 'ddd') == 'yes':
            # Do DDoS
            self.switch_ddd(state)
        self.app.log.info('Switch to state {} completed'.format(state))
    # end def switch_alerts( self, state ):

    def switch_ddd(self, state):
        self.dddSlave = FlowmonDDD(self.app, self.slave)
        slave = self.dddSlave.get_alerts()
        if self.master.connected:    
            self.dddMaster = FlowmonDDD(self.app, self.master)

        # check if we have alerts to set
        if slave:
            self.app.log.info('Performing switch over on DDD alerts')
            for alert in slave:
                conf = self.db.select_notification(alert['id'])
                cfg = list(conf)
                if state:
                    alert['sendSyslog'] = False
                    alert['sendSnmp'] = False
                    alert['sendEmail'] = False
                    if self.app.config.get('sync', 'mode') == 'passive':
                        alert['runScript'] = False
                    self.dddSlave.change_alert(alert)
                    self.app.log.debug(
                        'Updated alert {} - {}'.format(alert['id'], alert['name']))
                else:
                    alert['sendSyslog'] = True if cfg[2] else False
                    alert['sendSnmp'] = True if cfg[3] else False
                    alert['sendEmail'] = True if cfg[4] else False
                    alert['runScript'] = True if cfg[5] else False
                    self.dddSlave.change_alert(alert)
                    self.app.log.debug(
                        'Updated alert {} - {}'.format(alert['id'], alert['name']))
        # do the oposite operation on Master
        if self.master.connected:
            master = self.dddMaster.get_alerts()
            if master:
                self.app.log.info('Performing switch over on DDD alerts at master')
                for alert in master:
                    conf = self.db.select_master_notification(alert['id'])
                    cfg = list(conf)
                    if state:
                        alert['sendSyslog'] = True if cfg[2] else False
                        alert['sendSnmp'] = True if cfg[3] else False
                        alert['sendEmail'] = True if cfg[4] else False
                        alert['runScript'] = True if cfg[5] else False
                        self.dddMaster.change_alert(alert)
                        self.app.log.debug(
                            'Updated master alert {} - {}'.format(alert['id'], alert['name']))
                    else:
                        alert['sendSyslog'] = False
                        alert['sendSnmp'] = False
                        alert['sendEmail'] = False
                        if self.app.config.get('sync', 'mode') == 'passive':
                            alert['runScript'] = False
                        self.dddMaster.change_alert(alert)
                        self.app.log.debug(
                            'Updated master alert {} - {}'.format(alert['id'], alert['name']))
        
    # end def swtich_ddd(self, state):
    def switch_ads(self, state):
        adsSlave = FlowmonADS(self.app, self.slave)
        slave = adsSlave.get_event_reports()
        
        # check if there are alerts to change
        if slave:
            self.app.log.info('Performing switch over on ADS event reports')
            for email in slave:
                if state:
                    email['active'] = 0
                    adsSlave.change_event_report(email)
                    self.app.log.debug(
                        'Updated event report {} - {}'.format(email['id'], email['name']))
                else:
                    email['active'] = 1 if self.db.select_event_report_slave(email['id'])[0] else 0
                    adsSlave.change_event_report(email)
                    self.app.log.debug(
                        'Updated event report {} - {}'.format(email['id'], email['name']))
        # if we have a master connected let's perform the oposite switchover there
        if self.master.connected:
            adsMaster = FlowmonADS(self.app, self.master)
            master = adsMaster.get_event_reports()
            if master:
                self.app.log.info('Performing switch over of ADS event reports at master')
                for email in slave:
                    if state:
                        email['active'] = 1 if self.db.select_event_report_slave(email['id'])[0] else 0
                        adsMaster.change_event_report(email)
                        self.app.log.debug(
                            'Updated event report {} - {}'.format(email['id'], email['name']))
                    else:
                        email['active'] = 0
                        adsMaster.change_event_report(email)
                        self.app.log.debug(
                            'Updated event report {} - {}'.format(email['id'], email['name']))
    # end def switch_ads(self, state):

    def switch_fmc(self, state):
        slave = self.slave.get_emailreports()
        # check if we have report to set
        if slave:
            self.app.log.info('Performing switch over on FMC Reports emailing')
            for report in slave:
                conf = self.db.select_reporting(report['id'])
                cfg = list(conf)
                if state:
                    report['active'] = False
                    self.slave.change_emailreport(report)
                    self.app.log.debug(
                        'Updated emailing of report {} - {}'.format(report['id'], report['name']))
                else:
                    report['active'] = True if cfg[2] else False
                    self.slave.change_emailreport(report)
                    self.app.log.debug(
                        'Updated emailing of report {} - {}'.format(report['id'], report['name']))
        
        if self.master.connected:
        # now on master
            master = self.master.get_emailreports()
            # check if we have report to set
            if master:
                self.app.log.info('Performing switch over on FMC Reports emailing at master')
                for report in master:
                    conf = self.db.select_master_reporting(report['id'])
                    cfg = list(conf)
                    if state:
                        report['active'] = True if cfg[2] else False
                        self.master.change_emailreport(report)
                        self.app.log.debug(
                            'Updated master emailing of report {} - {}'.format(report['id'], report['name']))
                    else:
                        report['active'] = False
                        self.master.change_emailreport(report)
                        self.app.log.debug(
                            'Updated master emailing of report {} - {}'.format(report['id'], report['name']))

        slave = self.slave.get_alerts()
        # check if we have alerts to set
        if slave:
            self.app.log.info('Performing switch over on FMC alerts')
            for alert in slave:
                conf = self.db.select_alerting(alert['id'])
                cfg = list(conf)
                if state:
                    alert['definition']['reactions']['syslog']['enabled'] = 0
                    alert['definition']['reactions']['snmp']['enabled'] = 0
                    alert['definition']['reactions']['email']['enabled'] = 0
                    alert['definition']['reactions']['script']['enabled'] = 0
                    self.slave.change_alert(alert)
                    self.app.log.debug(
                        'Updated alert {} - {}'.format(alert['id'], alert['name']))
                else:
                    alert['definition']['reactions']['syslog']['enabled'] = cfg[2]
                    alert['definition']['reactions']['snmp']['enabled'] = cfg[3]
                    alert['definition']['reactions']['email']['enabled'] = cfg[4]
                    alert['definition']['reactions']['script']['enabled'] = cfg[5]
                    self.slave.change_alert(alert)
                    self.app.log.debug(
                        'Updated alert {} - {}'.format(alert['id'], alert['name']))

        if self.master.connected:
            master = self.master.get_alerts()
            # check if we have alerts to set
            if master:
                self.app.log.info('Performing switch over on FMC alerts')
                for alert in master:
                    conf = self.db.select_master_alerting(alert['id'])
                    cfg = list(conf)
                    if state:
                        alert['definition']['reactions']['syslog']['enabled'] = cfg[2]
                        alert['definition']['reactions']['snmp']['enabled'] = cfg[3]
                        alert['definition']['reactions']['email']['enabled'] = cfg[4]
                        alert['definition']['reactions']['script']['enabled'] = cfg[5]
                        self.master.change_alert(alert)
                        self.app.log.debug(
                            'Updated master alert {} - {}'.format(alert['id'], alert['name']))
                    else:
                        alert['definition']['reactions']['syslog']['enabled'] = 0
                        alert['definition']['reactions']['snmp']['enabled'] = 0
                        alert['definition']['reactions']['email']['enabled'] = 0
                        alert['definition']['reactions']['script']['enabled'] = 0
                        self.master.change_alert(alert)
                        self.app.log.debug(
                            'Updated master alert {} - {}'.format(alert['id'], alert['name']))
        # everything is done
    # end def switch_fmc(self, state):
