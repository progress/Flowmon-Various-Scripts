# Controll class to work with Flowmon API
from core.FlowmonREST import FlowmonREST
import re
import copy


class ControllFMC:

    def __init__(self, app, master, slave, func, db, first):
        self.app = app
        self.first = first
        self.master = master
        self.slave = slave
        self.func = func
        self.db = db

    def sync(self):
        version = self.master.get_version()
        if version:
            regex = r"(\d+)\.(\d+)\.(\d+)"
            match = re.search(regex, version['version'])
            if int(match.group(1)) >= 10:
                if int(match.group(2)) >= 3:
                    self.app.log.debug(
                        'FMC: Flowmon version over 10.3, will sync also roles and users')
                    self.roles()
                    # user sync disabled would need not encrypted password
                    # self.users()
                # we are not yet on 10.3
                self.bh()
                self.blacklists()
                self.profiles()
                self.fmc_chapters()
                self.fmc_reports()
                self.fmc_email()
                self.fmc_alerts()
            else:
                self.app.log.info(
                    'FMC: Flowmon version below 10.x, not planned for this version')
    # end def sync_fmc( self ):
    #
    # Function to sync FMC report chapters

    def fmc_alerts(self):
        self.app.log.info('FMC: Running FMC alerts configuration checks...')
        master = self.master.get_alerts()
        slave = self.slave.get_alerts()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'name', 'fmc_alert', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('FMC: Doing some modification on slave...')
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a role in DB
                    if self.db.select_fmc_alert(missing['id']) is None:
                        id = missing['id']
                        if self.db.select_profile(missing['definition']['profile']['id']) is not None:
                            missing['definition']['profile']['id'] = self.db.select_profile(
                                missing['definition']['profile']['id'])[0]
                        if missing['definition']['channels'] is not "*":
                            channels = []
                            for channel in missing['definition']['channels']:
                                if self.db.select_channel(channel['id']) is not None:
                                    channel['id'] = self.db.select_channel(channel['id'])[0]
                                    channel['name'] = channel['id']
                                channels.append(channel)
                            missing['definition']['channels'] = channels
                        syslog = int(missing['definition']
                                     ['reactions']['syslog']['enabled'])
                        snmp = int(missing['definition']
                                   ['reactions']['snmp']['enabled'])
                        email = int(missing['definition']
                                    ['reactions']['email']['enabled'])
                        script = int(missing['definition']
                                     ['reactions']['script']['enabled'])
                        if self.app.config.get('sync', 'syslog') == 'no':
                             missing['definition']['reactions']['syslog']['enabled'] = 0
                        missing['definition']['reactions']['snmp']['enabled'] = 0
                        missing['definition']['reactions']['email']['enabled'] = 0
                        missing['definition']['reactions']['script']['enabled'] = 0
                        del missing['currentState']
                        new = self.slave.add_alert(missing)
                        if not new == 0:
                            alert = (id, new['id'], syslog,
                                     snmp, email, script)
                            self.db.create_fmc_alert(alert)
                            self.app.log.debug(
                                'FMC: Added alert {} with ID {} '.format(new['name'], new['id']))
                    # change in name or IP
                    else:
                        missing['id'] = self.db.select_fmc_alert(missing['id'])[
                            0]
                        if self.db.select_profile(missing['definition']['profile']['id']) is not None:
                            missing['definition']['profile']['id'] = self.db.select_profile(
                                missing['definition']['profile']['id'])[0]
                        if missing['definition']['channels'] is not "*":
                            channels = []
                            for channel in missing['definition']['channels']:
                                if self.db.select_channel(channel['id']) is not None:
                                    channel['id'] = self.db.select_channel(channel['id'])[
                                        0]
                                    channel['name'] = channel['id']
                                channels.append(channel)
                            missing['definition']['channels'] = channels
                        syslog = int(missing['definition']
                                     ['reactions']['syslog']['enabled'])
                        snmp = int(missing['definition']
                                   ['reactions']['snmp']['enabled'])
                        email = int(missing['definition']
                                    ['reactions']['email']['enabled'])
                        script = int(missing['definition']
                                     ['reactions']['script']['enabled'])
                        if self.app.config.get('sync', 'syslog') == 'no':
                             missing['definition']['reactions']['syslog']['enabled'] = 0
                        missing['definition']['reactions']['snmp']['enabled'] = 0
                        missing['definition']['reactions']['email']['enabled'] = 0
                        missing['definition']['reactions']['script']['enabled'] = 0
                        del missing['currentState']
                        new = self.slave.change_alert(missing)
                        change = (syslog, snmp, email, script, missing['id'])
                        self.db.update_fmc_alert(change)
                        self.app.log.debug(
                            'FMC: Updating alert ID {}'.format(missing['id']))
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    if self.db.select_profile(updated['definition']['profile']['id']) is not None:
                        updated['definition']['profile']['id'] = self.db.select_profile(
                            updated['definition']['profile']['id'])[0]
                    if updated['definition']['channels'] is not "*":
                        channels = []
                        for channel in updated['definition']['channels']:
                            if self.db.select_channel(channel['id']) is not None:
                                channel['id'] = self.db.select_channel(channel['id'])[
                                    0]
                                channel['name'] = channel['id']
                            channels.append(channel)
                        updated['definition']['channels'] = channels
                    syslog = int(updated['definition']
                                 ['reactions']['syslog']['enabled'])
                    snmp = int(updated['definition']
                               ['reactions']['snmp']['enabled'])
                    email = int(updated['definition']
                                ['reactions']['email']['enabled'])
                    script = int(updated['definition']
                                 ['reactions']['script']['enabled'])
                    if self.app.config.get('sync', 'syslog') == 'no':
                        missing['definition']['reactions']['syslog']['enabled'] = 0
                    updated['definition']['reactions']['snmp']['enabled'] = 0
                    updated['definition']['reactions']['email']['enabled'] = 0
                    updated['definition']['reactions']['script']['enabled'] = 0
                    del updated['currentState']
                    new = self.slave.change_alert(updated)
                    change = (syslog, snmp, email, script, updated['id'])
                    self.db.update_fmc_alert(change)
                    self.app.log.debug(
                        'FMC: Updating alert ID {}'.format(updated['id']))
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug(
                        'FMC: Deleting alert ID {}'.format(deleted['id']))
                    self.slave.delete_alert(deleted['id'])
                    self.db.delete_fmc_alert(deleted['id'])
            else:
                self.app.log.info(
                    'FMC: Running full alerts sync with master. There are {} configuration items.'.format(len(master)))
                for item in master:
                    id = item['id']
                    del item['id']
                    if self.db.select_profile(item['definition']['profile']['id']) is not None:
                        item['definition']['profile']['id'] = self.db.select_profile(
                            item['definition']['profile']['id'])[0]
                    if item['definition']['channels'] is not "*":
                        channels = []
                        for channel in item['definition']['channels']:
                            if self.db.select_channel(channel['id']) is not None:
                                channel['id'] = self.db.select_channel(channel['id'])[
                                    0]
                                channel['name'] = channel['id']
                            channels.append(channel)
                        item['definition']['channels'] = channels
                    syslog = int(item['definition']
                                 ['reactions']['syslog']['enabled'])
                    snmp = int(item['definition']['reactions']
                               ['snmp']['enabled'])
                    email = int(item['definition']['reactions']
                                ['email']['enabled'])
                    script = int(item['definition']
                                 ['reactions']['script']['enabled'])
                    if self.app.config.get('sync', 'syslog') == 'no':
                        item['definition']['reactions']['syslog']['enabled'] = 0
                    item['definition']['reactions']['snmp']['enabled'] = 0
                    item['definition']['reactions']['email']['enabled'] = 0
                    item['definition']['reactions']['script']['enabled'] = 0
                    del item['currentState']
                    new = self.slave.add_alert(item)
                    if not new == 0:
                        alert = (id, new['id'], syslog, snmp, email, script)
                        self.db.create_fmc_alert(alert)
                        self.app.log.debug(
                            'Added alert {} with ID {} '.format(new['name'], new['id']))
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left chapters
                self.app.log.info(
                    'FMC: Master has no alerts but there are {} on slave, deleting...'.format(len(slave)))
                for item in slave:
                    self.slave.delete_alert(item['id'])
                    self.db.delete_fmc_alert(item['id'])
        self.app.log.info('FMC: Alerts section completed.')
    # end def fmc_alerts( self ):

    # Function to sync email reporting configuration
    def fmc_email(self):
        self.app.log.info('FMC: Running email reporting configuration check...')
        master = self.master.get_emailreports()
        slave = self.slave.get_emailreports()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'name', 'fmc_email', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('FMC: Doing some modification on slave...')
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really an alert in DB
                    if self.db.select_fmc_email(missing['id']) is None:
                        id = missing['id']
                        missing['id'] = None
                        active = missing['active']
                        missing['active'] = False
                        # Fix report ID
                        missing['report'] = self.db.select_fmc_email(missing['report'])[
                            0]
                        new = self.slave.add_emailreport(missing)
                        if not new == 0:
                            alert = (id, new['id'], active)
                            self.db.create_fmc_email(alert)
                            self.app.log.debug(
                                'FMC: Added email report {} with ID {} '.format(new['name'], new['id']))
                    # name has changed
                    else:
                        missing['id'] = self.db.select_fmc_email(missing['id'])[
                            0]
                        active = missing['active']
                        missing['active'] = False
                        # Fix report ID
                        missing['report'] = self.db.select_fmc_email(missing['report'])[
                            0]
                        self.slave.change_emailreport(missing)
                        change = (active, missing['id'])
                        self.db.update_fmc_email(change)
                        self.app.log.debug(
                            'FMC: Updating email report ID {}'.format(missing['id']))
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    active = missing['active']
                    missing['active'] = False
                    # Fix report ID
                    missing['report'] = self.db.select_fmc_email(missing['report'])[
                        0]
                    change = (active, missing['id'])
                    self.db.update_fmc_email(change)
                    jnew = self.slave.change_emailreport(updated)
                    if not jnew == 0:
                        self.app.log.debug(
                            'FMC: Updating email report ID {}'.format(updated['id']))
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug(
                        'FMC: Deleting email report ID {}'.format(deleted['id']))
                    self.slave.delete_emailreport(deleted['id'])
                    self.db.delete_fmc_email(deleted['id'])
            else:
                self.app.log.info(
                    'FMC: Running full email report sync with master. There are {} configuration items.'.format(len(master)))
                for fmc_email in master:
                    id = fmc_email['id']
                    fmc_email['id'] = None
                    active = fmc_email['active']
                    fmc_email['active'] = False
                    # Fix report ID
                    fmc_email['report'] = self.db.select_fmc_email(fmc_email['report'])[
                        0]
                    new = self.slave.add_emailreport(fmc_email)
                    if not new == 0:
                        email = (id, new['id'], active)
                        self.db.create_fmc_email(email)
                        self.app.log.debug(
                            'Added email report {} with ID {} '.format(new['name'], new['id']))
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left alerts
                self.app.log.info(
                    'FMC: Master has no email report but there are {} on slave, deleting...'.format(len(slave)))
                for fmc_email in slave:
                    self.app.log.debug(
                        'FMC: Deleting email report ID {}'.format(fmc_email['id']))
                    self.slave.delete_emailreport(fmc_email['id'])
                    self.db.delete_fmc_email(fmc_email['id'])
        self.app.log.info('FMC: Email alert section completed.')
    # end def fmc_email( self ):

    # Function to sync FMC report chapters
    def fmc_reports(self):
        self.app.log.info('FMC: Running reports configuration checks...')
        master = self.master.get_reports()
        slave = self.slave.get_reports()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'name', 'fmc_report', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('FMC: Doing some modification on slave...')
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a role in DB
                    if self.db.select_fmc_report(missing['id']) is None:
                        id = missing['id']
                        del missing['id']
                        chapters = []
                        for chapter in missing['chapters']:
                            chapter['chapterId'] = (
                                self.db.select_fmc_chapter(chapter['chapterId'])[0])
                            chapters.append(chapter)
                        missing['chapters'] = chapters
                        new = self.slave.add_report(missing)
                        if not new == 0:
                            self.db.create_fmc_report(id, new['id'])
                            self.app.log.debug(
                                'FMC: Added report {} with ID {} '.format(new['name'], new['id']))
                    # change in name or IP
                    else:
                        missing['id'] = self.db.select_fmc_chapter(missing['id'])[
                            0]
                        chapters = []
                        for chapter in missing['chapters']:
                            chapter['chapterId'] = (
                                self.db.select_fmc_chapter(chapter['chapterId'])[0])
                            chapters.append(chapter)
                        missing['chapters'] = chapters
                        new = self.slave.change_report(missing)
                        self.app.log.debug(
                            'FMC: Updating report ID {}'.format(missing['id']))
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    chapters = []
                    for chapter in updated['chapters']:
                        chapter['chapterId'] = self.db.select_fmc_chapter(chapter['chapterId'])[
                            0]
                        chapters.append(chapter)
                    updated['chapters'] = chapters
                    new = self.slave.change_report(updated)
                    self.app.log.debug(
                        'FMC: Updating report ID {}'.format(updated['id']))
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug(
                        'FMC: Deleting FMC report ID {}'.format(deleted['id']))
                    self.slave.delete_report(deleted['id'])
                    self.db.delete_fmc_report(deleted['id'])
            else:
                self.app.log.info(
                    'FMC: Running full reports sync with master. There are {} configuration items.'.format(len(master)))
                for item in master:
                    id = item['id']
                    item['id'] = None
                    chapters = []
                    for chapter in item['chapters']:
                        if self.db.select_fmc_chapter(chapter['chapterId']):
                            chapters.append(self.db.select_fmc_chapter(chapter['chapterId'])[0])
                    item['chapters'] = chapters
                    new = self.slave.add_chapter(item)
                    if not new == 0:
                        self.db.create_fmc_chapter(id, new['id'])
                        self.app.log.debug(
                            'FMC: Added report chapter {} with ID {} '.format(new['name'], new['id']))
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left chapters
                self.app.log.info(
                    'FMC: Master has no report chapters but there are {} on slave, deleting...'.format(len(slave)))
                for item in slave:
                    self.slave.delete_chapter(item['id'])
                    self.db.delete_fmc_chapter(item['id'])
        self.app.log.info('FMC: Report chapters section completed.')
    # end def fmc_reports( self ):

    # Function to sync FMC report chapters
    def fmc_chapters(self):
        self.app.log.info('FMC: Running report chapters configuration checks...')
        master = self.master.get_chapters()
        slave = self.slave.get_chapters()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'name', 'fmc_chapter', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('FMC: Doing some modification on slave...')
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a role in DB
                    if self.db.select_fmc_chapter(missing['id']) is None:
                        id = missing['id']
                        del missing['id']
                        if self.db.select_profile(missing['profile']) is not None:
                            missing['profile'] = self.db.select_profile(
                                missing['profile'])[0]
                        if missing['channels'] is not "*":
                            channels = []
                            for channel in missing['channels']:
                                channels.append(
                                    self.db.select_channel(channel)[0])
                            missing['channels'] = channels
                        new = self.slave.add_chapter(missing)
                        if not new == 0:
                            self.db.create_fmc_chapter(id, new['id'])
                            self.app.log.debug(
                                'FMC: Added report chapter {} with ID {} '.format(new['name'], new['id']))
                    # change in name or IP
                    else:
                        missing['id'] = self.db.select_fmc_chapter(missing['id'])[
                            0]
                        if missing['channels'] is not "*":
                            channels = []
                            for channel in missing['channels']:
                                channels.append(
                                    self.db.select_channel(channel)[0])
                            missing['channels'] = channels
                        new = self.slave.change_chapter(missing)
                        self.app.log.debug(
                            'FMC: Updating report chapter ID {}'.format(missing['id']))
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    if self.db.select_profile(updated['profile']) is not None:
                        updated['profile'] = self.db.select_profile(
                            updated['profile'])[0]
                    if updated['channels'] is not "*":
                        channels = []
                        for channel in updated['channels']:
                            channels.append(self.db.select_channel(channel)[0])
                        updated['channels'] = channels
                    new = self.slave.change_chapter(updated)
                    self.app.log.debug(
                        'FMC: Updating report chapter ID {}'.format(updated['id']))
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug(
                        'FMC: Deleting FMC chapter ID {}'.format(deleted['id']))
                    self.slave.delete_chapter(deleted['id'])
                    self.db.delete_fmc_chapter(deleted['id'])
            else:
                self.app.log.info(
                    'FMC: Running full report chapters sync with master. There are {} configuration items.'.format(len(master)))
                for item in master:
                    id = item['id']
                    item['id'] = None
                    new = self.slave.add_chapter(item)
                    if not new == 0:
                        self.db.create_fmc_chapter(id, new['id'])
                        self.app.log.debug(
                            'FMC: Added report chapter {} with ID {} '.format(new['name'], new['id']))
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left chapters
                self.app.log.info(
                    'FMC: Master has no report chapters but there are {} on slave, deleting...'.format(len(slave)))
                for item in slave:
                    self.slave.delete_chapter(item['id'])
                    self.db.delete_fmc_chapter(item['id'])
        self.app.log.info('FMC: Report chapters section completed.')
    # end def fmc_chapters( self ):

    # Function to sync blacklists configuration section of FCC
    def blacklists(self):
        self.app.log.info('FMC: Running blacklists configuration checks...')
        master = self.master.get_blacklists()
        slave = self.slave.get_blacklists()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'name', 'blacklist', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('FMC: Doing some modification on slave...')
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a role in DB
                    if self.db.select_blacklist(missing['id']) is None:
                        id = missing['id']
                        missing['id'] = None
                        new = self.slave.add_blacklist(missing)
                        if not new == 0:
                            self.db.create_blacklist(id, new['id'])
                            self.app.log.debug(
                                'FMC: Added blacklist {} with ID {} '.format(new['name'], new['id']))
                    # change in name or IP
                    else:
                        missing['id'] = self.db.select_blacklist(missing['id'])[
                            0]
                        new = self.slave.change_blacklist(missing)
                        self.app.log.debug(
                            'FMC: Updating blacklist ID {}'.format(missing['id']))
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    new = self.slave.change_blacklist(updated)
                    self.app.log.debug(
                        'FMC: Updating blacklist ID {}'.format(updated['id']))
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug(
                        'Deleting blacklist ID {}'.format(deleted['id']))
                    self.slave.delete_blacklist(deleted['id'])
                    self.db.delete_blacklist(deleted['id'])
            else:
                self.app.log.info(
                    'FMC: Running full blacklists sync with master. There are {} configuration items.'.format(len(master)))
                for item in master:
                    id = item['id']
                    item['id'] = None
                    new = self.slave.add_blacklist(item)
                    if not new == 0:
                        self.db.create_blacklist(id, new['id'])
                        self.app.log.debug(
                            'FMC: Added blacklist {} with ID {} '.format(new['name'], new['id']))
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left blacklists
                self.app.log.info(
                    'FMC: Master has no blacklists but there are {} on slave, deleting...'.format(len(slave)))
                for item in slave:
                    self.slave.delete_blacklist(item['id'])
                    self.db.delete_blacklist(item['id'])
        self.app.log.info('FMC: Blacklists section completed.')
    # end def blacklists( self ):

    # Function to sync business hours configuration section of FCC
    def bh(self):
        self.app.log.info('FMC: Running business hours configuration checks...')
        master = self.master.get_bh()
        slave = self.slave.get_bh()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'label', 'bh', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('FMC: Doing some modification on slave...')
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a role in DB
                    if self.db.select_bh(missing['id']) is None:
                        id = missing['id']
                        missing['id'] = None
                        new = self.slave.add_bh(missing)
                        if not new == 0:
                            self.db.create_bh(id, new['id'])
                            self.app.log.debug(
                                'FMC: Added business hours {} with ID {} '.format(new['label'], new['id']))
                    # change in name or IP
                    else:
                        missing['id'] = self.db.select_bh(missing['id'])[0]
                        new = self.slave.change_bh(missing)
                        self.app.log.debug(
                            'FMC: Updating business hours ID {}'.format(missing['id']))
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    new = self.slave.change_bh(updated)
                    self.app.log.debug(
                        'FMC: Updating business hours ID {}'.format(updated['id']))
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug(
                        'FMC: Deleting business hours ID {}'.format(deleted['id']))
                    self.slave.delete_bh(deleted['id'])
                    self.db.delete_bh(deleted['id'])
            else:
                self.app.log.info(
                    'FMC: Running full business hours sync with master. There are {} configuration items.'.format(len(master)))
                for item in master:
                    id = item['id']
                    item['id'] = None
                    new = self.slave.add_bh(item)
                    if not new == 0:
                        self.db.create_bh(id, new['id'])
                        self.app.log.debug(
                            'FMC: Added business hours {} with ID {} '.format(new['label'], new['id']))
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left business hours
                self.app.log.info(
                    'FMC: Master has no business hours but there are {} on slave, deleting...'.format(len(slave)))
                for item in slave:
                    self.slave.delete_bh(item['id'])
                    self.db.delete_bh(item['id'])
        self.app.log.info('FMC: Business hours section completed.')
    # end def bh( self ):

    # Function to sync roles configuration section of FCC
    def roles(self):
        self.app.log.info('FMC: Running roles configuration checks...')
        master = self.master.get_roles()
        slave = self.slave.get_roles()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'name', 'role', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('FMC: Doing some modification on slave...')
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a role in DB
                    if self.db.select_role(missing['id']) is None:
                        id = missing['id']
                        missing['id'] = None
                        new = self.slave.add_role(missing)
                        if not new == 0:
                            self.db.create_role(id, new['id'])
                            self.app.log.debug(
                                'FMC: Added role {} with ID {} '.format(new['name'], new['id']))
                    # change in name or IP
                    else:
                        missing['id'] = self.db.select_role(missing['id'])[0]
                        new = self.slave.change_role(missing)
                        self.app.log.debug(
                            'FMC: Updating role ID {}'.format(missing['id']))
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    new = self.slave.change_role(updated)
                    self.app.log.debug(
                        'FMC: Updating role ID {}'.format(updated['id']))
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug(
                        'FMC: Deleting role ID {}'.format(deleted['id']))
                    self.slave.delete_role(deleted['id'])
                    self.db.delete_role(deleted['id'])
            else:
                self.app.log.info(
                    'FMC: Running full roles sync with master. There are {} configuration items.'.format(len(master)))
                for item in master:
                    id = item['id']
                    item['id'] = None
                    new = self.slave.add_role(item)
                    if not new == 0:
                        self.db.create_role(id, new)
                        self.app.log.debug(
                            'FMC: Added role {} with ID {} '.format(new['name'], new['id']))
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left roles
                self.app.log.info(
                    'FMC: Master has no roles but there are {} on slave, deleting...'.format(len(slave)))
                for item in slave:
                    self.slave.delete_role(item['id'])
                    self.db.delete_role(item['id'])
        self.app.log.info('FMC: Roles section completed.')
    # end def roles( self ):

    # Function to sync users configuration section of FCC
    def users(self):
        self.app.log.info('FMC: Running users configuration checks...')
        master = self.master.get_users()
        slave = self.slave.get_users()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'login', 'user', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('FMC: Doing some modification on slave...')
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a role in DB
                    if self.db.select_user(missing['id']) is None:
                        id = missing['id']
                        missing['id'] = None
                        new = self.slave.add_user(missing)
                        if not new == 0:
                            self.db.create_user(id, new['id'])
                            self.app.log.debug(
                                'FMC: Added user {} with ID {} '.format(new['name'], new['id']))
                    # change in name or IP
                    else:
                        missing['id'] = self.db.select_user(missing['id'])[0]
                        new = self.slave.change_user(missing)
                        self.app.log.debug(
                            'FMC: Updating user ID {}'.format(missing['id']))
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    new = self.slave.change_user(updated)
                    self.app.log.debug(
                        'FMC: Updating user ID {}'.format(updated['id']))
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug(
                        'Deleting user ID {}'.format(deleted['id']))
                    self.slave.delete_user(deleted['id'])
                    self.db.delete_user(deleted['id'])
            else:
                self.app.log.info(
                    'FMC: Running full users sync with master. There are {} configuration items.'.format(len(master)))
                for item in master:
                    id = item['id']
                    item['id'] = None
                    new = self.slave.add_user(item)
                    if not new == 0:
                        self.db.create_user(id, new)
                        self.app.log.debug(
                            'FMC: Added user {} with ID {} '.format(new['name'], new['id']))
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left users
                self.app.log.info(
                    'FMC: Master has no users but there are {} on slave, deleting...'.format(len(slave)))
                for item in slave:
                    self.slave.delete_user(item['id'])
                    self.db.delete_user(item['id'])
        self.app.log.info('FMC: Users section completed.')
    # end def users( self ):

    # Function to sync profiles
    def profiles(self):
        self.app.log.info('FMC: Running profiles configuration checks...')
        master = self.master.get_profiles()
        for profile in master[:]:
            if profile.get("id", ) == "live":
                master.remove(profile)
            elif profile.get("group", ) == "Sources":
                master.remove(profile)
        slave = self.slave.get_profiles()
        for profile in slave[:]:
            if profile.get("id", ) == "live":
                slave.remove(profile)
            elif profile.get("group", ) == "Sources":
                slave.remove(profile)
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'name', 'profile', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('FMC: Doing some modification on slave...')
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a profile in DB
                    if self.db.select_profile(missing['id']) is None:
                        id = missing['id']
                        # Remove profile ID and end time
                        del missing['id']
                        del missing['end']
                        del missing['start']
                        if self.db.select_profile(missing['parent']) is not None:
                            missing['parent'] = self.db.select_profile(missing['parent'])[
                                0]
                        new = self.slave.add_profile(missing)
                        if not new == 0:
                            self.db.create_profile(id, new['id'])
                            self.app.log.debug(
                                'FMC: Added profile {} with ID {} '.format(new['name'], new['id']))
                            # fill DB with channels
                            for channel in new['channels']:
                                for orig in missing['channels']:
                                    if orig['name'] == channel['name']:
                                        self.db.create_channel(
                                            orig['id'], channel['id'])
                                        break
                    # change in name
                    else:
                        missing['id'] = self.db.select_profile(missing['id'])[
                            0]
                        modify = []
                        chmiss = []
                        for rrmast in missing['channels']:
                            if self.db.select_channel(rrmast['id']) is None:
                                chmiss.append(copy.deepcopy(rrmast))
                                del rrmast['id']
                            else:
                                rrmast['id'] = self.db.select_channel(rrmast['id'])[
                                    0]
                            modify.append(rrmast)
                        missing['channels'] = modify
                        if self.db.select_profile(missing['parent']) is not None:
                            missing['parent'] = self.db.select_profile(missing['parent'])[
                                0]
                        new = self.slave.change_profile(missing)
                        if not new == 0:
                            self.app.log.debug('FMC: Updating profile {} ID {}'.format(
                                missing['name'], missing['id']))
                            # add missing channels to DB
                            for channel in new['channels']:
                                for orig in chmiss:
                                    if orig['name'] == channel['name']:
                                        self.db.create_channel(
                                            orig['id'], channel['id'])
                                        break
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    modify = []
                    chmiss = []
                    for rrmast in updated['channels']:
                        if self.db.select_channel(rrmast['id']) is None:
                            chmiss.append(copy.deepcopy(rrmast))
                            del rrmast['id']
                        else:
                            rrmast['id'] = self.db.select_channel(rrmast['id'])[
                                0]
                        modify.append(rrmast)
                    updated['channels'] = modify
                    if self.db.select_profile(updated['parent']) is not None:
                        updated['parent'] = self.db.select_profile(updated['parent'])[
                            0]
                    new = self.slave.change_profile(updated)
                    if not new == 0:
                        self.app.log.debug('FMC: Updating profile {} ID {}'.format(
                            updated['name'], updated['id']))
                        # add missing channels to DB
                        for channel in new['channels']:
                            for orig in chmiss:
                                if orig['name'] == channel['name']:
                                    self.db.create_channel(
                                        orig['id'], channel['id'])
                                    break
                # And last delete all extra items
                for deleted in compare['deleted']:
                    for rrmast in deleted['channels']:
                        self.db.delete_channel(rrmast['id'])
                    if self.slave.delete_profile(deleted['id']):
                        self.app.log.debug('FMC: Deleted profile {} ID {}'.format(
                            deleted['name'], deleted['id']))
                    self.db.delete_profile(deleted['id'])
                    deleted['channels'] = modify
            else:
                self.app.log.info(
                    'FMC: Running full profile sync with master. There are {} configuration items.'.format(len(master)))
                for profile in master:
                    id = profile['id']
                    profile['id'] = None
                    del profile['end']
                    del profile['start']
                    if self.db.select_profile(profile['parent']) is not None:
                        profile['parent'] = self.db.select_profile(profile['parent'])[
                            0]
                    new = self.slave.add_profile(profile)
                    if not new == 0:
                        self.db.create_profile(id, new['id'])
                        self.app.log.debug(
                            'FMC: Added profile {} with ID {} '.format(new['name'], new['id']))
                        # fill DB have channels
                        for channel in new['channels']:
                            for orig in profile['channels']:
                                if orig['name'] == channel['name']:
                                    self.db.create_channel(
                                        orig['id'], channel['id'])
                                    break
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left users
                self.app.log.info(
                    'FMC: Master has no profiles but there are {} on slave, deleting...'.format(len(slave)))
                for item in slave:
                    for rrmast in item['channels']:
                        self.db.delete_channel(rrmast['id'])
                    if self.slave.delete_profile(item['id']):
                        self.app.log.debug('Deleted profile {} ID {}'.format(
                            item['name'], item['id']))
        self.app.log.info('FMC: Profiles section completed.')
    # end def profiles( self ):

    # here we switch between slave and master function
    # enable or disable alerting based on original master setup
    def switch_alerts(self, state):
        slave = self.slave.get_emailreports()
        # check if we have report to set
        if slave:
            self.app.log.info('FMC: Performing switch over on FMC Reports emailing')
            for report in slave:
                conf = self.db.select_reporting(report['id'])
                cfg = list(conf)
                if state:
                    report['active'] = False
                    self.slave.change_emailreport(report)
                    self.app.log.debug(
                        'FMC: Updated emailing of report {} - {}'.format(report['id'], report['name']))
                else:
                    report['active'] = True if cfg[2] else False
                    self.slave.change_emailreport(report)
                    self.app.log.debug(
                        'FMC: Updated emailing of report {} - {}'.format(report['id'], report['name']))

        slave = self.slave.get_alerts()
        # check if we have alerts to set
        if slave:
            self.app.log.info('FMC: Performing switch over on FMC alerts')
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
                        'FMC: Updated alert {} - {}'.format(alert['id'], alert['name']))
                else:
                    alert['definition']['reactions']['syslog']['enabled'] = cfg[2]
                    alert['definition']['reactions']['snmp']['enabled'] = cfg[3]
                    alert['definition']['reactions']['email']['enabled'] = cfg[4]
                    alert['definition']['reactions']['script']['enabled'] = cfg[5]
                    self.slave.change_alert(alert)
                    self.app.log.debug(
                        'FMC: Updated alert {} - {}'.format(alert['id'], alert['name']))
        self.app.log.info('FMC: Switch to state {} completed'.format(state))
    # end def switch_alerts( self, state ):
