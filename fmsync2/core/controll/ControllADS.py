# Controll class to work with Flowmon API
from core.FlowmonADS import FlowmonADS
import copy

class ControllADS:

    def __init__( self, app, master, slave, func, db, first ):
        self.app = app
        self.first = first
        self.master = master
        self.slave = slave
        self.func = func
        self.db = db

    # function to sync ADS configs
    def sync( self ):
        self.adsMaster = FlowmonADS(self.app, self.master)
        self.adsSlave = FlowmonADS(self.app, self.slave)
        self.feeds()
        self.filters()
        # There is an error with deletion. Would need to keep this disables for now.
        #self.false_positives()
        self.perspectives()
        self.methods()
        self.event_reports()
        # disabled the chapters for now as there is a bad JSON format in API
        #self.chapters()

    # first we need to sync data feeds configuration
    def feeds( self ):
        self.app.log.info( 'ADS: Running data feeds configuration checks...' )
        master = self.adsMaster.get_data_feeds()
        slave = self.adsSlave.get_data_feeds()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare( master, slave, 'name', 'data_feed', self.first )
            if compare == 1:
                #nothing to do here as we are good
                1
            elif compare:
                self.app.log.info( 'ADS: Doing some modification on slave...' )
                # First we add missing objects
                for missing in compare['missing']:
                    # Check if it isn't virtual (they are read-only)
                    if missing['virtual'] == 0:
                        # check if there isn't really a role in DB
                        if self.db.select_data_feed( missing['id'] ) is None:
                            id = missing['id']
                            if self.db.select_profile( missing['profile'] ) is not None:
                                missing['profile'] = self.db.select_profile( missing['profile'] )[0]
                            if missing['channels'] is not "*":
                                channels = []
                                for channel in missing['channels']:
                                    if self.db.select_channel( channel ) is not None:
                                        channel = self.db.select_channel( channel )[0]
                                    channels.append( channel )
                                missing['channels'] = channels
                            if missing['parentSource']:
                                df_id = self.db.select_data_feed(missing['parentSource']['id'])
                                if df_id is not None:
                                    missing['parentSource']['id'] = df_id[0]
                            new = self.adsSlave.add_data_feed( missing )
                            if not new == 0:
                                self.db.create_data_feed( id, new['id'] )
                                self.app.log.debug( 'ADS: Added data feed {} with ID {} '.format( new['name'], new['id'] ) )
                        # change in name
                        else:
                            missing['id'] = self.db.select_data_feed( missing['id'] )[0]
                            if self.db.select_profile(  missing['profile'] ) is not None:
                                missing['profile'] = self.db.select_profile( missing['profile'] )[0]
                            if missing['channels'] is not "*":
                                channels = []
                                for channel in missing['channels']:
                                    if self.db.select_channel( channel ) is not None:
                                        channel = self.db.select_channel( channel )[0]
                                    channels.append( channel )
                                missing['channels'] = channels
                            if missing['parentSource']:
                                df_id = self.db.select_data_feed(missing['parentSource']['id'])
                                if df_id is not None:
                                    missing['parentSource']['id'] = df_id[0]
                            new = self.adsSlave.change_data_feed( missing )
                            self.app.log.debug( 'ADS: Updating data feed {} ID {}'.format(missing['name'], missing['id']) )
                            # we also need to remove it from deleted if it exists there
                            for deleted in compare['deleted'][:]:
                                if deleted['id'] == missing['id']:
                                    compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    # Check if it isn't virtual (they are read-only)
                    if updated['virtual'] == 0:
                        if self.db.select_profile( updated['profile'] ) is not None:
                            updated['profile'] = self.db.select_profile( updated['profile'] )[0]
                        if updated['channels'] is not "*":
                            channels = []
                            for channel in updated['channels']:
                                channels.append( self.db.select_channel( channel )[0] )
                            updated['channels'] = channels
                        if updated['parentSource']:
                            df_id = self.db.select_data_feed(updated['parentSource']['id'])
                            if df_id is not None:
                                updated['parentSource']['id'] = df_id[0]
                        new = self.adsSlave.change_data_feed( updated )
                        self.app.log.debug( 'ADS: Updating data feed {} ID {}'.format(updated['name'], updated['id']) )
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug( 'ADS: Deleting data feed {} ID {}'.format(deleted['name'], deleted['id']) )
                    self.adsSlave.delete_data_feed( deleted['id'] )
                    self.db.delete_data_feed( deleted['id'] )
            else:
                self.app.log.info( 'ADS: Running full Data Feed sync with master. There are {} configuration items.'.format(len(master)) )
                for item in master:
                    # Check if it isn't virtual (they are read-only)
                    if item['virtual'] == 0:
                        id = item['id']
                        del item['id']
                        if self.db.select_profile( item['profile'] ) is not None:
                            item['profile'] = self.db.select_profile( item['profile'] )[0]
                        if item['channels'] is not "*":
                            channels = []
                            for channel in item['channels']:
                                if self.db.select_channel( channel ) is not None:
                                    channel = self.db.select_channel( channel )[0]
                                channels.append( channel )
                            item['channels'] = channels
                        if item['parentSource']:
                            df_id = self.db.select_data_feed(item['parentSource']['id'])
                            if df_id is not None:
                                item['parentSource']['id'] = df_id[0]
                        new = self.adsSlave.add_data_feed( item )
                        if not new == 0:
                            self.db.create_data_feed( id, new['id'] )
                            self.app.log.debug( 'ADS: Added Data Feed {} with ID {} '.format( new['name'], new['id'] ) )
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left data feeds
                self.app.log.info( 'ADS: Master has no data feeds but there are {} on slave, deleting...'.format(len(slave)) )
                for item in slave:
                    self.adsSlave.delete_data_feed( item['id'] )
                    self.db.delete_data_feed( item['id'] )
                    self.app.log.debug( 'ADS: Deleting data feed {} ID {}'.format(item['name'], item['id']) )
        self.app.log.info( 'ADS: Data feed section completed.' )
    #end def feeds( self ):

    # sync filters configuration
    def filters( self ):
        self.app.log.info( 'ADS: Running filters configuration checks...' )
        master = self.adsMaster.get_filters()
        slave = self.adsSlave.get_filters()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare( master, slave, 'name', 'filter', self.first )
            if compare == 1:
                #nothing to do here as we are good
                1
            elif compare:
                self.app.log.info( 'ADS: Doing some modification on slave...' )
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a role in DB
                    if self.db.select_filter( missing['id'] ) is None:
                        id = missing['id']
                        new = self.adsSlave.add_filter( missing )
                        if not new == 0:
                            self.db.create_filter( id, new['id'] )
                            self.app.log.debug( 'ADS: Added filter {} with ID {} '.format( new['name'], new['id'] ) )
                    # change in name
                    else:
                        missing['id'] = self.db.select_filter( missing['id'] )[0]
                        new = self.adsSlave.change_filter( missing )
                        self.app.log.debug( 'ADS: Updating filter {} ID {}'.format(missing['name'], missing['id']) )
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    new = self.adsSlave.change_filter( updated )
                    self.app.log.debug( 'ADS: Updating filter {} ID {}'.format(updated['name'], updated['id']) )
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug( 'ADS: Deleting filter {} ID {}'.format(deleted['name'], deleted['id']) )
                    self.adsSlave.delete_filter( deleted['id'] )
                    self.db.delete_filter( deleted['id'] )
            else:
                self.app.log.info( 'ADS: Running full filters sync with master. There are {} configuration items.'.format(len(master)) )
                for item in master:
                    id = item['id']
                    del item['id']
                    new = self.adsSlave.add_filter( item )
                    if not new == 0:
                        self.db.create_filter( id, new['id'] )
                        self.app.log.debug( 'ADS: Added filter {} with ID {} '.format( new['name'], new['id'] ) )
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left filters
                self.app.log.info( 'ADS: Master has no filters but there are {} on slave, deleting...'.format(len(slave)) )
                for item in slave:
                    self.adsSlave.delete_filter( item['id'] )
                    self.db.delete_filter( item['id'] )
                    self.app.log.debug( 'ADS: Deleting filter {} ID {}'.format(item['name'], item['id']) )
        self.app.log.info( 'ADS: Filters section completed.' )
    #end def filters( self ):

    # sync false-positives configuration
    def false_positives( self ):
        self.app.log.info( 'ADS: Running false-positives configuration checks...' )
        master = self.adsMaster.get_fps()
        slave = self.adsSlave.get_fps()
        if master:
            for item in master:
                # check if there isn't this FP rule already in DB
                if not self.db.select_fp( item['id'] ):
                    id = item['id']
                    # remove extra keys before adding the rule
                    del item['id']
                    del item['created']
                    del item['lastIgnored']
                    del item['usageChart']
                    # replace IDs with a proper one seen on slave
                    if item['sourceFilters']:
                        item['sourceFilters']['id'] = self.db.select_filter( item['sourceFilters']['id'] )
                    if item['targetFilters']:
                        item['targetFilters']['id'] = self.db.select_filter( item['targetFilters']['id'] )
                    if item['netFlowSources']:
                        item['netFlowSources']['id'] = self.db.select_data_feed( item['netFlowSources']['id'] )
                    new = self.adsSlave.add_fp( item )
                    if not new == 0:
                        self.db.create_fp( id, new['id'] )
                        self.app.log.debug( 'ADS: Added false-positive {} with ID {} '.format( new['code'], new['id'] ) )
                else:
                        slave_id = self.db.select_fp( item['id'] )[0]
                        slave_fp = self.adsSlave.get_fp( slave_id )
                        # remove it from array wiht slave configuration to remove these later if there are any deleted already
                        slave.remove(slave_fp)
                        # remove extra keys before comparing
                        del item['id']
                        del item['created']
                        del item['lastIgnored']
                        del item['usageChart']
                        del slave_fp['id']
                        del slave_fp['created']
                        del slave_fp['lastIgnored']
                        del slave_fp['usageChart']

                        if item != slave_fp:
                            # If they are different then we need to remove and add it as a new
                            self.app.log.debug( 'ADS: Deleting false-positive {} ID {}'.format(slave_fp['id'], slave_fp['id']) )
                            self.adsSlave.delete_fp( slave_fp['id'] )
                            self.db.delete_fp( slave_fp['id'] )
                            if item['sourceFilters']:
                                item['sourceFilters']['id'] = self.db.select_filter( item['sourceFilters']['id'] )
                            if item['targetFilters']:
                                item['targetFilters']['id'] = self.db.select_filter( item['targetFilters']['id'] )
                            if item['netFlowSources']:
                                item['netFlowSources']['id'] = self.db.select_data_feed( item['netFlowSources']['id'] )
                            new = self.adsSlave.add_fp( item )
                            if not new == 0:
                                self.db.create_fp( id, new['id'] )
                                self.app.log.debug( 'ADS: Added false-positive {} with ID {} '.format( new['code'], new['id'] ) )
            self.app.log.info( 'ADS: Deleting remainin false-positive rules. There are {} configuration items.'.format(len(slave)) )
            for item in slave:
                self.app.log.debug( 'ADS: Deleting false-positive {} ID {}'.format(item['code'], item['id']) )
                self.adsSlave.delete_fp( item['id'] )
                self.db.delete_fp( item['id'] )
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left filters
                self.app.log.info( 'ADS: Master has no false-positives but there are {} on slave, deleting...'.format(len(slave)) )
                for item in slave:
                    self.adsSlave.delete_fp( item['id'] )
                    self.db.delete_fp( item['id'] )
                    self.app.log.debug( 'ADS: Deleting false-positive {} ID {}'.format(item['code'], item['id']) )
        self.app.log.info( 'ADS: False-positives section completed.' )
    #end def false_positives( self ):

    # sync perspectives configuration
    def perspectives( self ):
        self.app.log.info( 'ADS: Running perspectives configuration checks...' )
        master = self.adsMaster.get_perspectives()
        slave = self.adsSlave.get_perspectives()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare( master, slave, 'name', 'perspective', self.first )
            if compare == 1:
                #nothing to do here as we are good
                1
            elif compare:
                self.app.log.info( 'ADS: Doing some modification on slave...' )
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a perspective in DB
                    if self.db.select_perspective( missing['id'] ) is None:
                        id = missing['id']
                        del missing['id']
                        for priority in missing['priorities']:
                            if priority['nfSource'] is not None:
                                priority['nfSource'] = self.db.select_data_feed( priority['nfSource']['id'] )[0]
                            if priority['filterIn'] is not None:
                                priority['filterIn'] = self.db.select_filter( priority['filterIn']['id'] )[0]
                            if priority['filterOut'] is not None:
                                priority['filterOut'] = self.db.select_filter( priority['filterOut']['id'] )[0]
                        new = self.adsSlave.add_perspective( missing )
                        if not new == 0:
                            self.db.create_perspective( id, new['id'] )
                            self.app.log.debug( 'ADS: Added perspective {} with ID {} '.format( new['name'], new['id'] ) )
                    # change in name
                    else:
                        missing['id'] = self.db.select_perspective( missing['id'] )[0]
                        for priority in missing['priorities']:
                            if priority['nfSource'] is not None:
                                priority['nfSource'] = self.db.select_data_feed( priority['nfSource']['id'] )[0]
                            if priority['filterIn'] is not None:
                                priority['filterIn'] = self.db.select_filter( priority['filterIn']['id'] )[0]
                            if priority['filterOut'] is not None:
                                priority['filterOut'] = self.db.select_filter( priority['filterOut']['id'] )[0]
                        new = self.adsSlave.change_perspective( missing )
                        self.app.log.debug( 'ADS: Updating perspective {} ID {}'.format(missing['name'], missing['id']) )
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    for priority in updated['priorities']:
                        if priority['nfSource'] is not None:
                            priority['nfSource'] = self.db.select_data_feed( priority['nfSource']['id'] )[0]
                        if priority['filterIn'] is not None:
                             priority['filterIn'] = self.db.select_filter( priority['filterIn']['id'] )[0]
                        if priority['filterOut'] is not None:
                            priority['filterOut'] = self.db.select_filter( priority['filterOut']['id'] )[0]
                    new = self.adsSlave.change_perspective( updated )
                    self.app.log.debug( 'ADS: Updating perspective {} ID {}'.format(updated['name'], updated['id']) )
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug( 'ADS: Deleting perspective {} ID {}'.format(deleted['name'], deleted['id']) )
                    self.adsSlave.delete_perspective( deleted['id'] )
                    self.db.delete_perspective( deleted['id'] )
            else:
                self.app.log.info( 'ADS: Running full perspective sync with master. There are {} configuration items.'.format(len(master)) )
                for item in master:
                    id = item['id']
                    del item['id']
                    for priority in item['priorities']:
                        if priority['nfSource'] is not None:
                            priority['nfSource'] = self.db.select_data_feed( priority['nfSource']['id'] )[0]
                        if priority['filterIn'] is not None:
                             priority['filterIn'] = self.db.select_filter( priority['filterIn']['id'] )[0]
                        if priority['filterOut'] is not None:
                            priority['filterOut'] = self.db.select_filter( priority['filterOut']['id'] )[0]
                    new = self.adsSlave.add_perspective( item )
                    if not new == 0:
                        self.db.create_perspective( id, new['id'] )
                        self.app.log.debug( 'ADS: Added perspective {} with ID {} '.format( new['name'], new['id'] ) )
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left perspectives
                self.app.log.info( 'ADS: Master has no perspectives but there are {} on slave, deleting...'.format(len(slave)) )
                for item in slave:
                    self.adsSlave.delete_perspective( item['id'] )
                    self.db.delete_perspective( item['id'] )
                    self.app.log.debug( 'ADS: Deleting perspective {} ID {}'.format(item['name'], item['id']) )
        self.app.log.info( 'ADS: Perspectives section completed.' )
    #end def perspectives( self ):

    # sync methods instances configuration
    def methods( self ):
        self.app.log.info( 'ADS: Running methods configuration checks...' )
        master = self.adsMaster.get_methods()
        slave = self.adsSlave.get_methods()
        if master and slave:
            # master section is not empty so we can run sync
            for method in master:
                for smethod in slave:
                    if method['code'] == smethod['code']:
                        if method['instances']:
                            # copy of instances on slave to delete any left overs
                            copy_sminst = copy.deepcopy(smethod['instances'])
                            # we have some instances on master
                            for instance in method['instances']:
                                if self.first:
                                    sid = False
                                else:
                                    sid = self.db.select_instance(instance['id'])
                                # is there instance in persistent DB
                                if sid:
                                    # it is so we need to check if there are any changes
                                    self.update_instance(instance['id'], sid[0])
                                    for sminst in smethod['instances']:
                                            if sminst['name'] == instance['name']:
                                                copy_sminst.remove(sminst)
                                else:
                                    if smethod['instances']:
                                        # we have instance for the the methods but they are not in the database
                                        # we need to find them and sync the DB
                                        minstance = self.adsMaster.get_instance(instance['id'])
                                        for sminst in smethod['instances']:
                                            if sminst['name'] == minstance['name']:
                                                copy_sminst.remove(sminst)
                                                # we found match by name
                                                self.db.create_instance( minstance['id'], sminst['id'], sminst['subId'] )
                                                self.update_instance(minstance['id'], sminst['id'])
                                            else:
                                                # not found match so lets create a new one
                                                self.create_instance(instance['id'])
                                    else:
                                        # no instance on Slave lets create this one    
                                        self.create_instance(instance['id'])
                            # there are some instances left on slave which were deleted from master
                            if copy_sminst:
                                for sminst in copy_sminst:
                                    self.adsSlave.delete_instance(sminst['id'])
                                    self.db.delete_instance(sminst['id'])
                                    self.app.log.debug( 'ADS: Deleted {} method instance {} with ID {} '.format( method['code'], sminst['name'], sminst['id'] ) )
                                   
                            break
                        else:
                            # There isn't an instance on master but there is one on slave
                            if smethod['instances'] is not None:
                                for instance in smethod['instances']:
                                    self.adsSlave.delete_instance(instance['id'])
                                    self.db.delete_instance(instance['id'])
                                    self.app.log.debug( 'ADS: Deleted {} method instance {} with ID {} '.format( method['code'], instance['name'], instance['id'] ) )
                                break
            self.app.log.info( 'ADS: Methods section completed.' )
        else:
            self.app.log.error( 'ADS: Methods section failed as systems cannot be contacted.' )
    #end def methods( self ):

    # To create ADS method instance on slave based on master configuration
    def create_instance(self, master_id):
        # Get master instance details because there isn't one on slave
        minstance = self.adsMaster.get_instance(master_id)
        if minstance['nfSources'] is not None:
            for source in minstance['nfSources']:
                source['id'] = self.db.select_data_feed( source['id'] )[0]
        if minstance['filters'] is not None:
            for filter in minstance['filters']:
                filter['id'] = self.db.select_filter( filter['id'] )[0]

        minstance['id'] = None
        minstance['subId'] = None
        for param in minstance['parameters']:
            param['id'] = None
            param['subId'] = None
        # now create a new instance of the method
        new = self.adsSlave.add_instance( minstance )
        if not new == 0:
            self.db.create_instance( master_id, new['id'], new['subId'] )
            self.app.log.debug( 'ADS: Added {} method instance {} with ID {} '.format( new['methodCode'], new['name'], new['id'] ) )
    #end def methods( self ):

    # Update the slave configuration of method instance if needed
    # needs both instances ID
    def update_instance(self, master_id, slave_id):
        change = 0
        minstance = self.adsMaster.get_instance(master_id)
        sinstance = self.adsSlave.get_instance(slave_id)
        if minstance['active'] != sinstance['active']:
            change = 1
            sinstance['active'] = minstance['active']
        if minstance['name'] != sinstance['name']:
            change = 1
            sinstance['name'] = minstance['name']
        if minstance['nfSources'] != sinstance['nfSources']:
            change = 1
            if minstance['nfSources'] is not None:
                for source in minstance['nfSources']:
                    source['id'] = self.db.select_data_feed( source['id'] )[0]
            sinstance['nfSources'] = minstance['nfSources']
        if minstance['filters'] != sinstance['filters']:
            change = 1
            if minstance['filters'] is not None:
                for filter in minstance['filters']:
                    filter['id'] = self.db.select_filter( filter['id'] )[0]
            sinstance['filters'] != minstance['filters']
        for mparam in minstance['parameters']:
            for sparam in sinstance['parameters']:
                if mparam['name'] == sparam['name']:
                    if mparam['value'] != sparam['value']:
                        change = 1
                        sparam['value'] =  mparam['value']
                    break
        if change:
            self.adsSlave.change_instance(sinstance)
            self.app.log.debug( 'ADS: Modified {} method instance {} with ID {} '.format( sinstance['methodCode'], sinstance['name'], sinstance['id'] ) )
        else:
            self.app.log.debug( 'ADS: Modification {} method instance {} with ID {} not needed'.format( sinstance['methodCode'], sinstance['name'], sinstance['id'] ) )
    #end def update_instance(self, master_id, slave_id):

    def event_reports(self):
        self.app.log.info( 'ADS: Running event reporting configuration checks...' )
        master = self.adsMaster.get_event_reports()
        slave = self.adsSlave.get_event_reports()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare( master, slave, 'name', 'event_report', self.first )
            if compare == 1:
                #nothing to do here as we are good
                1
            elif compare:
                self.app.log.info( 'ADS: Doing some modification on slave...' )
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a event report in DB
                    if self.db.select_event_report( missing['id'] ) is None:
                        id = missing['id']
                        del missing['id']
                        active = missing['active']
                        missing['active'] = 0
                        persp_id = self.db.select_perspective( missing['perspective']['id'] )
                        if persp_id is not None:
                            missing['perspective']['id'] = persp_id[0] 
                        new = self.adsSlave.add_event_report( missing )
                        if not new == 0:
                            self.db.create_event_report( id, new['id'], active )
                            self.app.log.debug( 'ADS: Added email event report {} with ID {} '.format( new['name'], new['id'] ) )
                    # change in name
                    else:
                        missing['id'] = self.db.select_event_report( missing['id'] )[0]
                        active = missing['active']
                        missing['active'] = 0
                        self.db.update_event_report( missing['id'], active )
                        persp_id = self.db.select_perspective( missing['perspective']['id'] )
                        if persp_id is not None:
                            missing['perspective']['id'] = persp_id[0] 
                        new = self.adsSlave.change_event_report( missing )
                        self.app.log.debug( 'ADS: Updating email event report ID {}'.format(missing['id']) )
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    active = updated['active']
                    updated['active'] = 0
                    self.db.update_event_report( updated['id'], active )
                    persp_id = self.db.select_perspective( updated['perspective']['id'] )
                    if persp_id is not None:
                        updated['perspective']['id'] = persp_id[0] 
                    new = self.adsSlave.change_event_report( updated )
                    self.app.log.debug( 'ADS: Updating email event report ID {}'.format(updated['id']) )
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug( 'ADS: Deleting email event report ID {}'.format(deleted['id']) )
                    self.adsSlave.delete_event_report( deleted['id'] )
                    self.db.delete_event_report( deleted['id'] )
            else:
                self.app.log.info( 'ADS: Running full email event report sync with master. There are {} configuration items.'.format(len(master)) )
                for item in master:
                    id = item['id']
                    del item['id']
                    active = item['active']
                    item['active'] = 0
                    persp_id = self.db.select_perspective( item['perspective']['id'] )
                    if persp_id:
                        item['perspective']['id'] = persp_id[0] 
                    new = self.adsSlave.add_event_report( item )
                    if not new == 0:
                        self.db.create_event_report( id, new['id'], active )
                        self.app.log.debug( 'ADS: Added email event report {} with ID {} '.format( new['name'], new['id'] ) )
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left filters
                self.app.log.info( 'ADS: Master has no email event reports but there are {} on slave, deleting...'.format(len(slave)) )
                for item in slave:
                    self.adsSlave.delete_event_report( item['id'] )
                    self.db.delete_event_report( item['id'] )
        self.app.log.info( 'ADS: Email event report section completed.' )
    #end def event_reports( self ):

    def chapters(self):
        self.app.log.info( 'ADS: Running PDF chapters configuration checks...' )
        master = self.adsMaster.get_chapters()
        slave = self.adsSlave.get_chapters()
        if master:
            # master section is not empty so we can run sync
            compare = self.func.compare( master, slave, 'name', 'chapter', self.first )
            if compare == 1:
                #nothing to do here as we are good
                1
            elif compare:
                self.app.log.info( 'ADS: Doing some modification on slave...' )
                # First we add missing objects
                for missing in compare['missing']:
                    # check if there isn't really a event report in DB
                    if self.db.select_ads_chapter( missing['id'] ):
                        id = missing['id']
                        del missing['id']
                        persp_id = self.db.select_perspective( missing['parameters']['perspective'] )
                        if persp_id is not None:
                            missing['parameters']['perspective'] = persp_id[0] 
                        new = self.adsSlave.add_chapter( missing )
                        if not new == 0:
                            self.db.create_ads_chapter( id, new['id'] )
                            self.app.log.debug( 'ADS: Added PDF chapter {} with ID {} '.format( new['name'], new['id'] ) )
                    # change in name
                    else:
                        missing['id'] = self.db.select_ads_chapter( missing['id'] )[0]
                        persp_id = self.db.select_perspective( missing['parameters']['perspective'] )
                        if persp_id is not None:
                            missing['parameters']['perspective'] = persp_id[0] 
                        new = self.adsSlave.change_chapter( missing )
                        self.app.log.debug( 'ADS: Updating PDF chapter {} with ID {}'.format(missing['name'], missing['id']) )
                        # we also need to remove it from deleted if it exists there
                        for deleted in compare['deleted'][:]:
                            if deleted['id'] == missing['id']:
                                compare['deleted'].remove(deleted)
                # Now let's modify existing one
                for updated in compare['updated']:
                    persp_id = self.db.select_perspective( updated['parameters']['perspective'] )
                    if persp_id is not None:
                        updated['parameters']['perspective'] = persp_id[0] 
                    new = self.adsSlave.change_chapter( updated )
                    self.app.log.debug( 'ADS: Updating PDF chapter {} with ID {}'.format(updated['name'], ['id']) )
                # And last delete all extra items
                for deleted in compare['deleted']:
                    self.app.log.debug( 'ADS: Deleting PDF chapter {} with ID {}'.format(deleted['name'], deleted['id']) )
                    self.adsSlave.delete_chapter( deleted['id'] )
                    self.db.delete_ads_chapter( deleted['id'] )
            else:
                self.app.log.info( 'ADS: Running full PDF chapter sync with master. There are {} configuration items.'.format(len(master)) )
                for item in master:
                    id = item['id']
                    del item['id']
                    persp_id = self.db.select_perspective( item['parameters']['perspective'] )
                    if persp_id is not None:
                        item['parameters']['perspective'] = persp_id[0] 
                    new = self.adsSlave.add_chapter( item )
                    if not new == 0:
                        self.db.create_ads_chapter( id, new['id'] )
                        self.app.log.debug( 'ADS: Added PDF chapter {} with ID {} '.format( new['name'], new['id'] ) )
        else:
            if slave:
                # master is empty but not slave
                # we woud need to delete all left filters
                self.app.log.info( 'ADS: Master has no PDF chapters but there are {} on slave, deleting...'.format(len(slave)) )
                for item in slave:
                    self.adsSlave.delete_chapter( item['id'] )
                    self.db.delete_ads_chapter( item['id'] )
        self.app.log.info( 'ADS: PDF chapter section completed.' )
    #end def event_reports( self ):
