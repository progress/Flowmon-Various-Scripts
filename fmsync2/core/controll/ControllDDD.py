# Controll class to work with Flowmon API
from core.FlowmonDDD import FlowmonDDD


class ControllDDD:

    def __init__(self, app, master, slave, func, db, first):
        self.app = app
        self.first = first
        self.master = master
        self.slave = slave
        self.func = func
        self.db = db
        self.version = 4

    def sync(self):
        self.dddMaster = FlowmonDDD(self.app, self.master)
        self.dddSlave = FlowmonDDD(self.app, self.slave)
        # check if we are running DDD version 5
        if self.dddMaster.get_groups() != 404:
            if self.dddSlave.get_groups() != 404:
                # we know both devices are running v5
                self.version = 5
            else:
                self.app.log.error('DDD: Master and slave version are not compatible!')
                return 1
        self.app.log.debug('DDD: Flowmon DDD api version {}'.format(self.version))
        self.routers()
        self.scrubbing()
        self.scrubbing_parametres()
        self.chapters()
        self.templates()
        self.alerts()
        self.custom_baselines()
        self.rules()
        if self.version == 5:
            self.groups()
        self.segments()
        # we need to the whitelists as the last since they depend on segements and groups
        self.whitelists()
    # end def sync( self ):

    # Function to sync groups configuration section of DDD
    def groups(self):
        self.app.log.info('DDD: Running groups configuration checks...')
        master = self.dddMaster.get_groups()
        slave = self.dddSlave.get_groups()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'name', 'group', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('DDD: Doing some modification on slave...')
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a group in DB
                    if self.db.select_group(missing['id']) is None:
                        id = missing['id']
                        missing['id'] = None
                        new = self.dddSlave.add_group(missing)
                        if not new == 0:
                            self.db.create_group(id, new['id'])
                            self.app.log.debug(
                                'DDD: Added group {} with ID {} '.format(new['name'], new['id']))
                    # change in name or IP
                    else:
                        missing['id'] = self.db.select_group(missing['id'])[0]
                        new = self.dddSlave.change_group(missing)
                        self.app.log.debug(
                            'DDD: Updating group ID {}'.format(missing['id']))
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    new = self.dddSlave.change_group(updated)
                    self.app.log.debug(
                        'DDD: Updating group ID {}'.format(updated['id']))
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug(
                        'DDD: Deleting group ID {}'.format(deleted['id']))
                    self.dddSlave.delete_group(deleted['id'])
                    self.db.delete_group(deleted['id'])
            else:
                self.app.log.info(
                    'DDD: Running full groups sync with master. There are {} configuration items.'.format(len(master)))
                for group in master:
                    id = group['id']
                    group['id'] = None
                    new = self.dddSlave.add_group(group)
                    if not new == 0:
                        self.db.create_group(id, new['id'])
                        self.app.log.debug(
                            'DDD: Added group {} with ID {} '.format(new['name'], new['id']))
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left groups
                self.app.log.info(
                    'DDD: Master has no groups but there are {} on slave, deleting...'.format(len(slave)))
                for group in slave:
                    self.dddSlave.delete_group(group['id'])
                    self.db.delete_group(group['id'])
        self.app.log.info('DDD: Groups section completed.')
    # end def groups( self ):

    # Function to sync routers configuration section of DDD
    def routers(self):
        self.app.log.info('DDD: Running routers configuration checks...')
        master = self.dddMaster.get_routers()
        slave = self.dddSlave.get_routers()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'ip', 'router', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('DDD: Doing some modification on slave...')
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a router in DB
                    if self.db.select_router(missing['id']) is None:
                        id = missing['id']
                        missing['id'] = None
                        new = self.dddSlave.add_router(missing)
                        if not new == 0:
                            self.db.create_router(id, new['id'])
                            self.app.log.debug(
                                'DDD: Added router {} with ID {} '.format(new['name'], new['id']))
                    # change in name or IP
                    else:
                        missing['id'] = self.db.select_router(missing['id'])[0]
                        new = self.dddSlave.change_router(missing)
                        self.app.log.debug(
                            'DDD: Updating router ID {}'.format(missing['id']))
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    new = self.dddSlave.change_router(updated)
                    self.app.log.debug(
                        'DDD: Updating router ID {}'.format(updated['id']))
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug(
                        'DDD: Deleting router ID {}'.format(deleted['id']))
                    self.dddSlave.delete_router(deleted['id'])
                    self.db.delete_router(deleted['id'])
            else:
                self.app.log.info(
                    'DDD: Running full routers sync with master. There are {} configuration items.'.format(len(master)))
                for router in master:
                    id = router['id']
                    router['id'] = None
                    new = self.dddSlave.add_router(router)
                    if not new == 0:
                        self.db.create_router(id, new['id'])
                        self.app.log.debug(
                            'DDD: Added router {} with ID {} '.format(new['name'], new['id']))
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left routers
                self.app.log.info(
                    'DDD: Master has no routers but there are {} on slave, deleting...'.format(len(slave)))
                for router in slave:
                    self.dddSlave.delete_router(router['id'])
                    self.db.delete_router(router['id'])
        self.app.log.info('DDD: Routers section completed.')
    # end def routers( self ):

    # Function to sync scrubbing configuration
    def scrubbing(self):
        self.app.log.info('DDD: Running scrubbing-center configuration check...')
        master = self.dddMaster.get_scrubbing()
        slave = self.dddSlave.get_scrubbing()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'ip', 'scrubbing', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('DDD: Doing some modification on slave...')
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a template in DB
                    if self.db.select_scrubbing(missing['id']) is None:
                        id = missing['id']
                        missing['id'] = None
                        new = self.dddSlave.add_scrubbing(missing)
                        if not new == 0:
                            self.db.create_scrubbing(id, new['id'])
                            self.app.log.debug(
                                'DDD: Added scrubbing-center {} with ID {} '.format(new['name'], new['id']))
                        else:
                            missing['id'] = self.db.select_scrubbing(missing['id'])[
                                0]
                            jnew = self.dddSlave.change_scrubbing(missing)
                            if not jnew == 0:
                                self.app.log.debug(
                                    'DDD: Updating scrubbing-center ID {}'.format(missing['id']))
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    jnew = self.dddSlave.change_scrubbing(updated)
                    self.app.log.debug(
                        'DDD: Updating scrubbing-center ID {}'.format(updated['id']))
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug(
                        'DDD: Deleting scrubbing center ID {}'.format(deleted['id']))
                    self.dddSlave.delete_scrubbing(deleted['id'])
                    self.db.delete_scrubbing(deleted['id'])
            else:
                self.app.log.info(
                    'DDD: Running full scrubbing-center sync with master. There are {} configuration items.'.format(len(master)))
                for scrubbing in master:
                    id = scrubbing['id']
                    scrubbing['id'] = None
                    new = self.dddSlave.add_scrubbing(scrubbing)
                    if not new == 0:
                        self.db.create_scrubbing(id, new['id'])
                        self.app.log.debug(
                            'DDD: Added scrubbing-center {} with ID {} '.format(new['name'], new['id']))
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left routers
                self.app.log.info(
                    'DDD: Master has no scrubbing-center but there are {} on slave, deleting...'.format(len(slave)))
                for scrubbing in slave:
                    self.dddSlave.delete_scrubbing(scrubbing['id'])
                    self.db.delete_scrubbing(scrubbing['id'])
        self.app.log.info('DDD: Scrubbing-center section completed.')
    # end def scrubbing( self ):

    # Function to sync alerts configuration
    def alerts(self):
        self.app.log.info('DDD: Running alerts configuration check...')
        master = self.dddMaster.get_alerts()
        slave = self.dddSlave.get_alerts()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'name', 'alert', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('DDD: Doing some modification on slave...')
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really an alert in DB
                    if self.db.select_alert(missing['id']) is None:
                        id = missing['id']
                        missing['id'] = None
                        syslog = missing['sendSyslog']
                        snmp = missing['sendSnmp']
                        email = missing['sendEmail']
                        script = missing['runScript']
                        if self.app.config.get('sync', 'syslog') == 'no':
                            missing['sendSyslog'] = False
                        missing['sendSnmp'] = False
                        missing['sendEmail'] = False
                        if self.app.config.get('sync', 'mode') == 'passive':
                            missing['runScript'] = False
                        # Fix template ID
                        if missing['template']:
                            if self.db.select_template(missing['template']['id']) is not None:
                                missing['template']['id'] = self.db.select_template(
                                    missing['template']['id'])[0]
                        new = self.dddSlave.add_alert(missing)
                        if not new == 0:
                            alert = (id, new['id'], syslog,
                                     snmp, email, script)
                            self.db.create_alert(alert)
                            self.app.log.debug(
                                'DDD: Added alert {} with ID {} '.format(new['name'], new['id']))
                    # name has changed
                    else:
                        missing['id'] = self.db.select_alert(missing['id'])[0]
                        syslog = missing['sendSyslog']
                        snmp = missing['sendSnmp']
                        email = missing['sendEmail']
                        script = missing['runScript']
                        if self.app.config.get('sync', 'syslog') == 'no':
                            missing['sendSyslog'] = False
                        missing['sendSnmp'] = False
                        missing['sendEmail'] = False
                        if self.app.config.get('sync', 'mode') == 'passive':
                            missing['runScript'] = False
                        # Fix template ID
                        if missing['template']:
                            if self.db.select_template(missing['template']['id']) is not None:
                                missing['template']['id'] = self.db.select_template(
                                    missing['template']['id'])[0]
                        self.dddSlave.change_alert(missing)
                        change = (syslog, snmp, email, script, missing['id'])
                        self.db.update_alert(change)
                        self.app.log.debug(
                            'DDD: Updating alert ID {}'.format(missing['id']))
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    self.app.log.debug(
                        'DDD: Updating alert ID {}'.format(updated['id']))
                    syslog = updated['sendSyslog']
                    snmp = updated['sendSnmp']
                    email = updated['sendEmail']
                    script = updated['runScript']
                    if self.app.config.get('sync', 'syslog') == 'no':
                        updated['sendSyslog'] = False
                    updated['sendSnmp'] = False
                    updated['sendEmail'] = False
                    if self.app.config.get('sync', 'mode') == 'passive':
                        updated['runScript'] = False
                    # Fix template ID
                    if updated['template']:
                        if self.db.select_template(updated['template']['id']) is not None:
                            updated['template']['id'] = self.db.select_template(
                                updated['template']['id'])[0]
                    change = (syslog, snmp, email, script, updated['id'])
                    jnew = self.db.update_alert(change)
                    if not jnew == 0:
                        jnew = self.dddSlave.change_alert(updated)
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug(
                        'DDD: Deleting alert ID {}'.format(deleted['id']))
                    self.dddSlave.delete_alert(deleted['id'])
                    self.db.delete_alert(deleted['id'])
            else:
                self.app.log.info(
                    'DDD: Running full alerts sync with master. There are {} configuration items.'.format(len(master)))
                for alert in master:
                    id = alert['id']
                    alert['id'] = None
                    syslog = alert['sendSyslog']
                    snmp = alert['sendSnmp']
                    email = alert['sendEmail']
                    script = alert['runScript']
                    if self.app.config.get('sync', 'syslog') == 'no':
                        alert['sendSyslog'] = False
                    alert['sendSnmp'] = False
                    alert['sendEmail'] = False
                    if self.app.config.get('sync', 'mode') == 'passive':
                        alert['runScript'] = False
                    # Fix template ID
                    if alert['template']:
                        if self.db.select_template(alert['template']['id']) is not None:
                            alert['template']['id'] = self.db.select_template(
                                alert['template']['id'])[0]
                    new = self.dddSlave.add_alert(alert)
                    if not new == 0:
                        data = (id, new['id'], syslog, snmp, email, script)
                        self.db.create_alert(data)
                        self.app.log.debug(
                            'DDD: Added alert {} with ID {} '.format(new['name'], new['id']))
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left alerts
                self.app.log.info(
                    'DDD: Master has no alerts but there are {} on slave, deleting...'.format(len(slave)))
                for alert in slave:
                    self.dddSlave.delete_alert(alert['id'])
                    self.db.delete_alert(alert['id'])
        self.app.log.info('DDD: Alerts section completed.')
    # end def alerts( self ):

    # Function to sync alerts configuration
    def scrubbing_parametres(self):
        self.app.log.info(
            'DDD: Running scrubbing-center parameters configuration check...')
        master = self.dddMaster.get_scrubbing_parameters()
        slave = self.dddSlave.get_scrubbing_parameters()
        if master:
            # master section is not empty so we can run sync
            if master == slave:
                self.app.log.debug('DDD: Scrubbing-center parameters are the same')
            else:
                self.dddSlave.change_scrubbing_parametres(master)
        self.app.log.info('DDD: Scrubbing-center parameters section completed.')
    # end def scrubbing_parametres( self ):

    # Function to sync report chapters configuration section of DDD
    def chapters(self):
        self.app.log.info('DDD: Running report chapters configuration checks...')
        master = self.dddMaster.get_report_chapters()
        slave = self.dddSlave.get_report_chapters()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'name', 'chapter', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('DDD: Doing some modification on slave...')
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a chapter in DB
                    if self.db.select_chapter(missing['id']) is None:
                        id = missing['id']
                        missing['id'] = None
                        new = self.dddSlave.add_chapter(missing)
                        if not new == 0:
                            self.db.create_chapter(id, new['id'])
                            self.app.log.debug(
                                'DDD: Added chapter {} with ID {} '.format(new['name'], new['id']))
                    # new name of chapter
                    else:
                        missing['id'] = self.db.select_chapter(missing['id'])[
                            0]
                        self.app.log.debug(
                            'DDD: Updating chapter ID {}'.format(missing['id']))
                        new = self.dddSlave.change_chapter(missing)
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)

                # Now let's modify existing one
                for updated in compare['updated']:
                    self.app.log.debug(
                        'DDD: Updating chapter ID {}'.format(updated['id']))
                    new = self.dddSlave.change_chapter(updated)
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug(
                        'DDD: Deleting DDD chapter ID {}'.format(deleted['id']))
                    self.dddSlave.delete_chapter(deleted['id'])
                    self.db.delete_chapter(deleted['id'])
            else:
                self.app.log.info(
                    'DDD: Running full report chapter sync with master. There are {} configuration items.'.format(len(master)))
                for chapter in master:
                    id = chapter['id']
                    chapter['id'] = None
                    new = self.dddSlave.add_chapter(chapter)
                    if not new == 0:
                        self.db.create_chapter(id, new['id'])
                        self.app.log.debug(
                            'DDD: Added chapter {} with ID {} '.format(new['name'], new['id']))
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left chapters
                self.app.log.info(
                    'DDD: Master has no chapters but there are {} on slave, deleting...'.format(len(slave)))
                for chapter in slave:
                    self.dddSlave.delete_chapter(chapter['id'])
                    self.db.delete_chapter(chapter['id'])
        self.app.log.info('DDD: Report chapters section completed.')
    # end def chapters( self ):

    # Function to sync email templates configuration section of DDD
    def templates(self):
        self.app.log.info('DDD: Running email templates configuration checks...')
        master = self.dddMaster.get_email_templates()
        slave = self.dddSlave.get_email_templates()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'name', 'template', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('DDD: Doing some modification on slave...')
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a template in DB
                    if self.db.select_template(missing['id']) is None:
                        id = missing['id']
                        missing['id'] = None
                        new = self.dddSlave.add_template(missing)
                        if not new == 0:
                            self.db.create_template(id, new['id'])
                            self.app.log.debug(
                                'DDD: Added email template {} with ID {} '.format(new['name'], new['id']))
                    # new name of template
                    else:
                        missing['id'] = self.db.select_template(missing['id'])[0]
                        self.app.log.debug(
                            'DDD: Updating email template ID {}'.format(missing['id']))
                        new = self.dddSlave.change_template(missing)
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    self.app.log.debug(
                        'DDD: Updating email template ID {}'.format(updated['id']))
                    new = self.dddSlave.change_template(updated)
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug(
                        'DDD: Deleting template ID {}'.format(deleted['id']))
                    self.dddSlave.delete_template(deleted['id'])
                    self.db.delete_template(deleted['id'])
            else:
                self.app.log.info(
                    'DDD: Running full email template sync with master. There are {} configuration items.'.format(len(master)))
                for template in master:
                    id = template['id']
                    template['id'] = None
                    new = self.dddSlave.add_template(template)
                    if not new == 0:
                        self.db.create_template(id, new['id'])
                        self.app.log.debug(
                            'DDD: Added email template {} with ID {} '.format(new['name'], new['id']))
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left templates
                self.app.log.info(
                    'DDD: Master has no email templates but there are {} on slave, deleting...'.format(len(slave)))
                for template in slave:
                    self.dddSlave.delete_template(template['id'])
                    self.db.delete_template(template['id'])
        self.app.log.info('DDD: Email templates section completed.')
    # end def templates( self ):

    # Function to sync ruless configuration section of DDD
    def rules(self):
        self.app.log.info('DDD: Running rules configuration checks...')
        master = self.dddMaster.get_rules()
        slave = self.dddSlave.get_rules()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'name', 'rule', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('DDD: Doing some modification on slave...')
                # First we add missing objects
                self.app.log.debug(
                    'DDD: There are {} new rules'.format(len(compare['missing'])))
                for missing in compare['missing']:
                    # check if there isn't really a rule in DB
                    if self.db.select_rule(missing['id']) is None:
                        id = missing['id']
                        del missing['id']
                        new = self.dddSlave.add_rule(missing)
                        if not new == 0:
                            self.db.create_rule(id, new['id'])
                            self.app.log.debug(
                                'DDD: Added rule {} with ID {} '.format(new['name'], new['id']))
                    # name has changed
                    else:
                        missing['id'] = self.db.select_rule(missing['id'])[0]
                        self.dddSlave.change_rule(missing)
                        self.app.log.debug(
                            'DDD: Updating rule ID {}'.format(missing['id']))
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                self.app.log.debug(
                    'DDD: There are {} modified rules'.format(len(compare['updated'])))
                for updated in compare['updated']:
                    new = self.dddSlave.change_rule(updated)
                    if not new == 0:
                        self.app.log.debug(
                            'DDD: Updating rule ID {}'.format(updated['id']))
                # And last delete all extra items
                self.app.log.debug(
                    'DDD: There are {} extra rules'.format(len(compare['deleted'])))
                for deleted in compare['deleted']:
                    self.app.log.debug(
                        'DDD: Deleting rule ID {}'.format(deleted['id']))
                    self.dddSlave.delete_rule(deleted['id'])
                    self.db.delete_rule(deleted['id'])
            else:
                self.app.log.info(
                    'DDD: Running full rules sync with master. There are {} configuration items.'.format(len(master)))
                for rule in master:
                    id = rule['id']
                    rule['id'] = None
                    new = self.dddSlave.add_rule(rule)
                    if not new == 0:
                        self.db.create_rule(id, new['id'])
                        self.app.log.debug(
                            'DDD: Added rule {} with ID {} '.format(new['name'], new['id']))
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left rules
                self.app.log.info(
                    'DDD: Master has no rules but there are {} on slave, deleting...'.format(len(slave)))
                for rule in slave:
                    self.dddSlave.delete_rule(rule['id'])
                    self.db.delete_rule(rule['id'])
        self.app.log.info('DDD: Rules section completed.')
    # end def rules( self ):

    # Function to sync segments configuration section of DDD
    def segments(self):
        self.app.log.info('DDD: Running segments configuration checks...')
        master = self.dddMaster.get_segments()
        slave = self.dddSlave.get_segments()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'name', 'segment', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('DDD: Doing some modification on slave...')
                # First we add missing objects
                self.app.log.debug(
                    'DDD: There are {} new segments'.format(len(compare['missing'])))
                for missing in compare['missing']:
                    # check if there isn't really a segment in DB
                    if self.db.select_segment(missing['id']) is None:
                        id = missing['id']
                        missing['id'] = None
                        missing['rule']['id'] = self.get_rule_id(
                            missing['rule']['name'])
                        if missing['measures']['alert']:
                            missing['measures']['alert']['id'] = self.get_alert_id(
                                missing['measures']['alert']['name'])
                        # to reroute we need to add routerId
                        rrnew = []
                        if 'reroute' in missing['measures'] and missing['measures']['reroute']:
                            for rrmast in missing['measures']['reroute']:
                                if rrmast['routerName'] is not None:
                                    rrmast['routerId'] = self.get_router_id(
                                        rrmast['routerName'])
                                rrnew.append(rrmast)
                        missing['measures']['reroute'] = rrnew
                        if self.version == 4:
                            if self.db.select_profile(missing['parentProfile']['profile']) is not None:
                                missing['parentProfile']['profile'] = self.db.select_profile(
                                    missing['parentProfile']['profile'])[0]
                                if missing['parentProfile']['channels'] is not "*":
                                    channels = []
                                    for channel in missing['parentProfile']['channels']:
                                        if self.db.select_channel(channel) is not None:
                                            channels.append(
                                                self.db.select_channel(channel)[0])
                                        else:
                                            channels.append(channel)
                                    missing['parentProfile']['channels'] = channels

                        missing['whitelists'] = []        

                        new = self.dddSlave.add_segment(missing)
                        if not new == 0:
                            self.db.create_segment(id, new['id'])
                            self.app.log.debug(
                                'DDD: Added segment {} with ID {} '.format(new['name'], new['id']))
                    # perhaps there was a change of name
                    else:
                        missing['id'] = self.db.select_segment(missing['id'])[0]
                        missing['rule']['id'] = self.get_rule_id(
                            missing['rule']['name'])
                        if missing['measures']['alert']:
                            missing['measures']['alert']['id'] = self.get_alert_id(
                                missing['measures']['alert']['name'])
                        # to reroute we need to add routerId
                        rrnew = []
                        if 'reroute' in missing['measures'] and missing['measures']['reroute']:
                            for rrmast in missing['measures']['reroute']:
                                if rrmast['routerName'] is not None:
                                    rrmast['routerId'] = self.get_router_id(
                                        rrmast['routerName'])
                                rrnew.append(rrmast)
                        missing['measures']['reroute'] = rrnew
                        if self.version == 4:
                            if self.db.select_profile(missing['parentProfile']['profile']) is not None:
                                missing['parentProfile']['profile'] = self.db.select_profile(
                                    missing['parentProfile']['profile'])[0]
                                if missing['parentProfile']['channels'] is not "*":
                                    channels = []
                                    for channel in missing['parentProfile']['channels']:
                                        if self.db.select_channel(channel) is not None:
                                            channels.append(
                                                self.db.select_channel(channel)[0])
                                        else:
                                            channels.append(channel)
                                    missing['parentProfile']['channels'] = channels

                        missing['whitelists'] = []
                        # Do not reset baseline
                        missing['resetBaseline'] = False

                        new = self.dddSlave.change_segment(missing)
                        if not new == 0:
                            self.app.log.debug(
                                'DDD: Updated segment {} with ID {} '.format(new['name'], new['id']))
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Then delete all extra items
                self.app.log.debug(
                    'DDD: There are {} deleted segments'.format(len(compare['deleted'])))
                for deleted in compare['deleted']:
                    self.app.log.debug(
                        'DDD: Deleted segment ID {}'.format(deleted['id']))
                    self.dddSlave.delete_segment(deleted['id'])
                    self.db.delete_segment(deleted['id'])
                # As a last step modify existing to make sure there are not going to be some issues because of overlapping segments
                self.app.log.debug(
                    'DDD: There are {} updated segments'.format(len(compare['updated'])))
                for updated in compare['updated']:
                    updated['rule']['id'] = self.get_rule_id(
                        updated['rule']['name'])
                    if updated['measures']['alert']:
                        updated['measures']['alert']['id'] = self.get_alert_id(
                            updated['measures']['alert']['name'])
                    # to reroute we need to add routerId
                    rrnew = []
                    if 'reroute' in updated['measures'] and updated['measures']['reroute']:
                        for rrmast in updated['measures']['reroute']:
                            if rrmast['routerName'] is not None:
                                rrmast['routerId'] = self.get_router_id(
                                    rrmast['routerName'])
                            rrnew.append(rrmast)
                    updated['measures']['reroute'] = rrnew
                    if self.version == 4:
                        if self.db.select_profile(updated['parentProfile']['profile']) is not None:
                            updated['parentProfile']['profile'] = self.db.select_profile(
                                updated['parentProfile']['profile'])[0]
                            if updated['parentProfile']['channels'] is not "*":
                                channels = []
                                for channel in updated['parentProfile']['channels']:
                                    if self.db.select_channel(channel) is not None:
                                        channels.append(
                                            self.db.select_channel(channel)[0])
                                    else:
                                        channels.append(channel)
                                updated['parentProfile']['channels'] = channels

                    updated['whitelists'] = []
                    # Do not reset baseline
                    updated['resetBaseline'] = False

                    new = self.dddSlave.change_segment(updated)
                    if not new == 0:
                        self.app.log.debug('DDD: Updated segment {} with  ID {}'.format(
                            updated['name'], updated['id']))
            else:
                self.app.log.info(
                    'DDD: Running full segments sync with master. There are {} configuration items.'.format(len(master)))
                for segment in master:
                    id = segment['id']
                    segment['id'] = None
                    segment['rule']['id'] = self.get_rule_id(
                        segment['rule']['name'])
                    if segment['measures']['alert']:
                        segment['measures']['alert']['id'] = self.get_alert_id(
                            segment['measures']['alert']['name'])
                    # to reroute we need to add routerId
                    rrnew = []
                    if 'reroute' in segment['measures'] and segment['measures']['reroute']:
                        for rrmast in segment['measures']['reroute']:
                            if rrmast['routerName'] is not None:
                                rrmast['routerId'] = self.get_router_id(
                                    rrmast['routerName'])
                            rrnew.append(rrmast)
                    segment['measures']['reroute'] = rrnew
                    if self.version == 4:
                        if self.db.select_profile(segment['parentProfile']['profile']) is not None:
                            segment['parentProfile']['profile'] = self.db.select_profile(
                                segment['parentProfile']['profile'])[0]
                            if segment['parentProfile']['channels'] is not "*":
                                channels = []
                                for channel in segment['parentProfile']['channels']:
                                    if self.db.select_channel(channel) is not None:
                                        channels.append(
                                            self.db.select_channel(channel)[0])
                                    else:
                                        channels.append(channel)
                                segment['parentProfile']['channels'] = channels

                    segment['whitelists'] = []
                    new = self.dddSlave.add_segment(segment)
                    if not new == 0:
                        self.db.create_segment(id, new['id'])
                        self.app.log.debug(
                            'DDD: Added segment {} with ID {} '.format(new['name'], new['id']))
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left segmnents
                self.app.log.info(
                    'DDD: Master has no segments but there are {} on slave, deleting...'.format(len(slave)))
                for segment in slave:
                    self.dddSlave.delete_segment(segment['id'])
                    self.db.delete_segment(segment['id'])
        self.app.log.info('DDD: Segments section completed.')
    # end def segments( self ):

    # function to find rule ID on slave to match the master config
    def get_rule_id(self, name):
        rules = self.dddSlave.get_rules()
        match = None
        for rule in rules:
            if rule['name'] == name:
                match = rule['id']
                break

        return match
    # end def get_rule_id ( self, name ):

    # function to find alert ID on slave to match the master config
    def get_alert_id(self, name):
        alerts = self.dddSlave.get_alerts()
        match = None
        for alert in alerts:
            if alert['name'] == name:
                match = alert['id']
                break

        return match
    # end def get_alert_id ( self, name ):

    # function to find router ID on slave to match the master config
    def get_router_id(self, name):
        routers = self.dddSlave.get_routers()
        match = None
        for router in routers:
            if router['name'] == name:
                match = router['id']
                break

        return match
    # end def get_router_id ( self, name ):

    def switch_alerts(self, state):
        slave = self.dddSlave.get_alerts()
        # check if we have alerts to set
        if slave:
            self.app.log.info('DDD: Performing switch over on DDD alerts')
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
                        'DDD: Updated alert {} - {}'.format(alert['id'], alert['name']))
                else:
                    alert['sendSyslog'] = True if cfg[2] else False
                    alert['sendSnmp'] = True if cfg[3] else False
                    alert['sendEmail'] = True if cfg[4] else False
                    alert['runScript'] = True if cfg[5] else False
                    self.dddSlave.change_alert(alert)
                    self.app.log.debug(
                        'DDD: Updated alert {} - {}'.format(alert['id'], alert['name']))

    # Function to sync custom baseline configuration section of DDD
    def custom_baselines(self):
        self.app.log.info('DDD: Running custom baselines configuration checks...')
        master = self.dddMaster.get_custombaselines()
        slave = self.dddSlave.get_custombaselines()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'name', 'custom_baseline', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('DDD: Doing some modification on slave...')
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a custom baseline in DB
                    if self.db.select_custom_baseline(missing['id']) is None:
                        id = missing['id']
                        missing['id'] = None
                        new = self.dddSlave.add_custombaseline(missing)
                        if not new == 0:
                            self.db.create_custom_baseline(id, new['id'])
                            self.app.log.debug(
                                'DDD: Added custom baseline {} with ID {} '.format(new['name'], new['id']))
                    # new name of baseline
                    else:
                        missing['id'] = self.db.select_custom_baseline(missing['id'])[
                            0]
                        self.app.log.debug(
                            'DDD: Updating custom baseline ID {}'.format(missing['id']))
                        new = self.dddSlave.change_custombaseline(missing)
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)

                # Now let's modify existing one
                for updated in compare['updated']:
                    self.app.log.debug(
                        'DDD: Updating custom baseline ID {}'.format(updated['id']))
                    new = self.dddSlave.change_custombaseline(updated)
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug(
                        'DDD: Deleting DDD custom baseline ID {}'.format(deleted['id']))
                    self.dddSlave.delete_custombaseline(deleted['id'])
                    self.db.delete_custom_baseline(deleted['id'])
            else:
                self.app.log.info(
                    'DDD: Running full custom baseline sync with master. There are {} configuration items.'.format(len(master)))
                for chapter in master:
                    id = chapter['id']
                    chapter['id'] = None
                    new = self.dddSlave.add_custombaseline(chapter)
                    if not new == 0:
                        self.db.create_custom_baseline(id, new['id'])
                        self.app.log.debug(
                            'DDD: Added custom baseline {} with ID {} '.format(new['name'], new['id']))
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left custom baselines
                self.app.log.info(
                    'DDD: Master has no custom baselines but there are {} on slave, deleting...'.format(len(slave)))
                for chapter in slave:
                    self.dddSlave.delete_custombaseline(chapter['id'])
                    self.db.delete_custom_baseline(chapter['id'])
        self.app.log.info('DDD: Custom baseliness section completed.')
    # end def custom_baselines( self ):

    # Function to sync whitelists configuration section of DDD
    def whitelists(self):
        self.app.log.info('DDD: Running whitelists configuration checks...')
        master = self.dddMaster.get_whitelists()
        slave = self.dddSlave.get_whitelists()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare(
                master, slave, 'name', 'whitelist', self.first)
            if compare == 1:
                # nothing to do here as we are good
                1
            elif compare:
                self.app.log.info('DDD: Doing some modification on slave...')
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a whitelist in DB
                    if self.db.select_whitelist(missing['id']) is None:
                        id = missing['id']
                        missing['id'] = None
                        # we need to fix a segment ids
                        if missing['whitelistedSegments']:
                            for wlmast in missing['whitelistedSegments']:
                                wlmast['id'] = self.db.select_segment(wlmast['id'])[0]
                        # we need to fix a group ids
                        if missing['whitelistedGroups']:
                            for wlmast in missing['whitelistedGroups']:
                                wlmast['id'] = self.db.select_segment(wlmast['id'])[0]
                        # to traffic types we need to add id
                        if missing['whitelistedTrafficTypes']:
                            for ttype in missing['whitelistedTrafficTypes']:
                                if ttype['name'] is not None:
                                    ttype['id'] = self.get_traffic_id(ttype['name'])
                        new = self.dddSlave.add_whitelist(missing)
                        if not new == 0:
                            self.db.create_whitelist(id, new['id'])
                            self.app.log.debug(
                                'DDD: Added whitelist {} with ID {} '.format(new['name'], new['id']))
                    # new name of baseline
                    else:
                        missing['id'] = self.db.select_whitelist(missing['id'])[0]
                        # we need to fix a segment ids
                        if missing['whitelistedSegments']:
                            for wlmast in missing['whitelistedSegments']:
                                wlmast['id'] = self.db.select_segment(wlmast['id'])[0]
                        # we need to fix a group ids
                        if missing['whitelistedGroups']:
                            for wlmast in missing['whitelistedGroups']:
                                wlmast['id'] = self.db.select_segment(wlmast['id'])[0]
                        # to traffic types we need to add id
                        if missing['whitelistedTrafficTypes']:
                            for ttype in missing['whitelistedTrafficTypes']:
                                if ttype['name'] is not None:
                                    ttype['id'] = self.get_traffic_id(ttype['name'])
                        self.app.log.debug(
                            'DDD: Updating whitelist ID {}'.format(missing['id']))
                        new = self.dddSlave.change_whitelist(missing)
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)

                # Now let's modify existing one
                for updated in compare['updated']:
                    self.app.log.debug(
                        'DDD: Updating whitelist ID {}'.format(updated['id']))
                    # we need to fix a segment ids
                    if updated['whitelistedSegments']:
                        for wlmast in updated['whitelistedSegments']:
                            wlmast['id'] = self.db.select_segment(wlmast['id'])[0]
                    # we need to fix a group ids
                    if updated['whitelistedGroups']:
                        for wlmast in updated['whitelistedGroups']:
                            wlmast['id'] = self.db.select_segment(wlmast['id'])[0]
                    # to traffic types we need to add id
                    if updated['whitelistedTrafficTypes']:
                        for ttype in updated['whitelistedTrafficTypes']:
                            if ttype['name'] is not None:
                                ttype['id'] = self.get_traffic_id(ttype['name'])
                    new = self.dddSlave.change_whitelist(updated)
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug(
                        'DDD: Deleting DDD whitelist ID {}'.format(deleted['id']))
                    self.dddSlave.delete_whitelist(deleted['id'])
                    self.db.delete_whitelist(deleted['id'])
            else:
                self.app.log.info(
                    'DDD: Running full whitelist sync with master. There are {} configuration items.'.format(len(master)))
                for chapter in master:
                    id = chapter['id']
                    chapter['id'] = None
                    # we need to fix a segment ids
                    if chapter['whitelistedSegments']:
                        for wlmast in chapter['whitelistedSegments']:
                            wlmast['id'] = self.db.select_segment(wlmast['id'])[0]
                    # we need to fix a group ids
                    if chapter['whitelistedGroups']:
                        for wlmast in chapter['whitelistedGroups']:
                            wlmast['id'] = self.db.select_segment(wlmast['id'])[0]
                    # to traffic types we need to add id
                    if chapter['whitelistedTrafficTypes']:
                        for ttype in chapter['whitelistedTrafficTypes']:
                            if ttype['name'] is not None:
                                ttype['id'] = self.get_traffic_id(ttype['name'])
                    new = self.dddSlave.add_whitelist(chapter)
                    if not new == 0:
                        self.db.create_whitelist(id, new['id'])
                        self.app.log.debug(
                            'DDD: Added whitelist {} with ID {} '.format(new['name'], new['id']))
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left whitelists
                self.app.log.info(
                    'DDD: Master has no whitelists but there are {} on slave, deleting...'.format(len(slave)))
                for chapter in slave:
                    self.dddSlave.delete_whitelist(chapter['id'])
                    self.db.delete_whitelist(chapter['id'])
        self.app.log.info('DDD: whitelistss section completed.')
    # end def whitelists( self ):

    # function to find traffic type ID on slave to match the master config
    def get_traffic_id(self, name):
        ttypes = self.dddSlave.get_traffictypes()
        match = None
        for ttype in ttypes:
            if ttype['name'] == name:
                match = ttype['id']
                break
        return match
    # end def get_traffic_id ( self, name ):