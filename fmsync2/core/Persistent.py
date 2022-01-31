import sqlite3
from sqlite3 import Error
import os.path


class Persistent:
    """
    This part is to keep information about IDs to be able to delete and modify the existing even in case of
    changes in names and or IPs and their mapping.
    Also, we keep the alerts sestting in file to make sure we can switch between master and slave state.
    """
    STDV = '/data/components/fmsync2/state/fmsync.db'

    def __init__(self, app):
        self.app = app
        if os.path.isfile(self.STDV) and os.path.getsize(self.STDV) > 0:
            self.conn = self.create_connection()
        else:
            self.conn = self.create_connection()
            self.db_init()
            self.app.log.debug('Database initalized')

    def create_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.STDV, isolation_level=None)
            self.app.log.debug(
                'SQLite3 version connected: {}'.format(sqlite3.version))
        except Error as e:
            self.app.log.error('Connection to DB failed: {}'.format(e))

        return conn

    def create_table(self, table_sql):
        try:
            c = self.conn.cursor()
            c.execute(table_sql)
        except Error as e:
            self.app.log.error('Cannot create a table: {}'.format(e))

    def db_init(self):
        sql_create_segments = """CREATE TABLE IF NOT EXISTS segments (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        sql_create_alerts = """CREATE TABLE IF NOT EXISTS alerts (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL,
                                    syslog integer,
                                    snmp integer,
                                    email integer,
                                    script integer
                                );"""

        sql_create_templates = """CREATE TABLE IF NOT EXISTS templates (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        sql_create_routers = """CREATE TABLE IF NOT EXISTS routers (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        sql_create_scrubbing = """CREATE TABLE IF NOT EXISTS scrubbing (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        sql_create_reports = """CREATE TABLE IF NOT EXISTS reports (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        sql_create_rules = """CREATE TABLE IF NOT EXISTS rules (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        sql_create_state = """CREATE TABLE IF NOT EXISTS state (
                                    slave integer NOT NULL
                                );"""

        sql_create_roles = """CREATE TABLE IF NOT EXISTS roles (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        sql_create_users = """CREATE TABLE IF NOT EXISTS users (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        sql_create_profiles = """CREATE TABLE IF NOT EXISTS profiles (
                                    id integer PRIMARY KEY,
                                    master text NOT NULL,
                                    slave text NOT NULL
                                );"""

        sql_create_channels = """CREATE TABLE IF NOT EXISTS channels (
                                    id integer PRIMARY KEY,
                                    master text NOT NULL,
                                    slave text NOT NULL
                                );"""

        sql_create_bh = """CREATE TABLE IF NOT EXISTS bhs (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        sql_create_blacklists = """CREATE TABLE IF NOT EXISTS blacklists (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        sql_create_fmc_chapters = """CREATE TABLE IF NOT EXISTS fmc_chapters (
                                    id integer PRIMARY KEY,
                                    master text NOT NULL,
                                    slave text NOT NULL
                                );"""

        sql_create_fmc_reports = """CREATE TABLE IF NOT EXISTS fmc_reports (
                                    id integer PRIMARY KEY,
                                    master text NOT NULL,
                                    slave text NOT NULL
                                );"""

        sql_create_fmc_emails = """CREATE TABLE IF NOT EXISTS fmc_emails (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL,
                                    active integer
                                );"""

        sql_create_fmc_alerts = """CREATE TABLE IF NOT EXISTS fmc_alerts (
                                    id text PRIMARY KEY,
                                    slave text NOT NULL,
                                    syslog integer,
                                    snmp integer,
                                    email integer,
                                    script integer
                                );"""

        sql_create_data_feed = """CREATE TABLE IF NOT EXISTS data_feed (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        sql_create_filters = """CREATE TABLE IF NOT EXISTS filters (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        sql_create_fps = """CREATE TABLE IF NOT EXISTS fps (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        sql_create_methods = """CREATE TABLE IF NOT EXISTS methods (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        sql_create_instances = """CREATE TABLE IF NOT EXISTS instances (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL,
                                    subId integer NOT NULL
                                );"""

        sql_create_event_reports = """CREATE TABLE IF NOT EXISTS event_reports (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL,
                                    active integer
                                );"""

        sql_create_ads_chapters = """CREATE TABLE IF NOT EXISTS ads_chapters (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        sql_create_perspectives = """CREATE TABLE IF NOT EXISTS perspectives (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        sql_create_groups = """CREATE TABLE IF NOT EXISTS groups (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        sql_create_custom_baselines = """CREATE TABLE IF NOT EXISTS custom_baselines (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        sql_create_whitelists = """CREATE TABLE IF NOT EXISTS whitelists (
                                    id integer PRIMARY KEY,
                                    slave integer NOT NULL
                                );"""

        if self.conn is not None:
            self.create_table(sql_create_segments)
            self.create_table(sql_create_alerts)
            self.create_table(sql_create_templates)
            self.create_table(sql_create_routers)
            self.create_table(sql_create_scrubbing)
            self.create_table(sql_create_reports)
            self.create_table(sql_create_rules)
            self.create_table(sql_create_state)
            self.create_table(sql_create_roles)
            self.create_table(sql_create_users)
            self.create_table(sql_create_profiles)
            self.create_table(sql_create_channels)
            self.create_table(sql_create_bh)
            self.create_table(sql_create_blacklists)
            self.create_table(sql_create_fmc_chapters)
            self.create_table(sql_create_fmc_reports)
            self.create_table(sql_create_fmc_emails)
            self.create_table(sql_create_fmc_alerts)
            self.create_table(sql_create_data_feed)
            self.create_table(sql_create_filters)
            self.create_table(sql_create_fps)
            self.create_table(sql_create_methods)
            self.create_table(sql_create_instances)
            self.create_table(sql_create_perspectives)
            self.create_table(sql_create_event_reports)
            self.create_table(sql_create_ads_chapters)
            self.create_table(sql_create_groups)
            self.create_table(sql_create_custom_baselines)
            self.create_table(sql_create_whitelists)
            self.create_state()
            self.app.log.info('Persistent DB initialized')
        else:
            self.app.log.error('Connection to database is not established')
    # end def db_init( self ):

    def create_group(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO groups(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_group( self, master, slave ):

    def select_group(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM groups WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_group( self, id ):

    def delete_group(self, master):
        sql = 'DELETE FROM groups WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_group( self, master ):

    def create_perspective(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO perspectives(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_perspective( self, master, slave ):

    def select_perspective(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM perspectives WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_perspective( self, id ):

    def delete_perspective(self, master):
        sql = 'DELETE FROM perspectives WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_perspective( self, master ):

    def create_fp(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO fps(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_fp( self, master, slave ):

    def select_fp(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM fps WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_fp( self, id ):

    def delete_fp(self, master):
        sql = 'DELETE FROM fps WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_fp( self, master ):

    def create_method(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO methods(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_method( self, master, slave ):

    def select_method(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM methods WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_method( self, id ):

    def delete_method(self, master):
        sql = 'DELETE FROM methods WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_method( self, master ):

    def create_instance(self, master, slave, subId):
        entry = (master, slave, subId)
        sql = 'INSERT INTO instances(id,slave, subId) VALUES(?,?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_instance( self, master, slave, subId ):

    def select_instance(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave, subId FROM instances WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_instance( self, id ):

    def delete_instance(self, master):
        sql = 'DELETE FROM instances WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_instance( self, master ):

    def create_filter(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO filters(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_filter( self, master, slave ):

    def select_filter(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM filters WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_filter( self, id ):

    def delete_filter(self, master):
        sql = 'DELETE FROM filters WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_filter( self, master ):

    def create_data_feed(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO data_feed(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_data_feed( self, master, slave ):

    def select_data_feed(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM data_feed WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_data_feed( self, id ):

    def delete_data_feed(self, master):
        sql = 'DELETE FROM data_feed WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_data_feed( self, master ):    
     
    def create_event_report(self, master, slave, active):
        entry = (master, slave, active)
        sql = 'INSERT INTO event_reports(id,slave,active) VALUES(?,?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_event_report(self, master, slave, active):

    def update_event_report(self, slave, data):
        sql = 'UPDATE event_reports SET active = ? WHERE slave = ?;'
        cur = self.conn.cursor()
        cur.execute(sql, (slave,data))
    # end def update_event_report( self, data ):

    def select_event_report(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave, active FROM event_reports WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_event_report( self, id ):

    def select_event_report_slave(self, slave):
        cur = self.conn.cursor()
        cur.execute('SELECT active FROM event_reports WHERE slave=?', (slave,))
        return cur.fetchone()
    # end def select_event_report_slave( self, slave ):

    def delete_event_report(self, master):
        sql = 'DELETE FROM event_reports WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_event_report( self, master ):

    def create_ads_chapter(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO ads_chapters(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_ads_chapter( self, master, slave ):

    def select_ads_chapter(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM ads_chapters WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_ads_chapter( self, id ):

    def delete_ads_chapter(self, master):
        sql = 'DELETE FROM ads_chapters WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_ads_chapter( self, master ):  

    def create_segment(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO segments(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_segment( self, master, slave ):

    def select_segment(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM segments WHERE id=?', (id,))
        record = cur.fetchone()
        return record
    # end def select_segment( self, id ):

    def delete_segment(self, master):
        sql = 'DELETE FROM segments WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_segment( self, master ):

    def create_report(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO reports(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_report( self, master, slave ):

    def select_report(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM reports WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_report( self, id ):

    def delete_report(self, master):
        sql = 'DELETE FROM reports WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_report( self, master ):

    def create_rule(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO rules(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_rule( self, master, slave ):

    def select_rule(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM rules WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_rule( self, id ):

    def delete_rule(self, master):
        sql = 'DELETE FROM rules WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_rule( self, master ):

    def create_scrubbing(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO scrubbing(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_scrubbing( self, master, slave ):

    def select_scrubbing(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM scrubbing WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_scrubbing( self, id ):

    def delete_scrubbing(self, master):
        sql = 'DELETE FROM scrubbing WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_scrubbing( self, master ):

    def create_router(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO routers(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_router( self, master, slave ):

    def select_router(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM routers WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_router( self, id ):

    def delete_router(self, master):
        sql = 'DELETE FROM routers WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_router( self, master ):

    def create_template(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO templates(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_template( self, master, slave ):

    def select_template(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM templates WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_template( self, id ):

    def delete_template(self, master):
        sql = 'DELETE FROM templates WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_template( self, master ):

    def create_alert(self, data):
        # convert data types
        lst = list(data)
        if lst[2]:
            lst[2] = 1
        else:
            lst[2] = 0
        if lst[3]:
            lst[3] = 1
        else:
            lst[3] = 0
        if lst[4]:
            lst[4] = 1
        else:
            lst[4] = 0
        if lst[5]:
            lst[5] = 1
        else:
            lst[5] = 0
        data = tuple(lst)

        sql = 'INSERT INTO alerts(id,slave,syslog,snmp,email,script) VALUES(?,?,?,?,?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, data)
        return cur.lastrowid
    # end def create_alert( self, data ):

    def delete_alert(self, slave):
        sql = 'DELETE FROM alerts WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (slave,))
    # end def delete_alert( self, slave ):

    def select_alert(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM alerts WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_alert( self, id ):

    def select_notification(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM alerts WHERE slave=?', (id,))
        return cur.fetchone()
    # end def select_notification( self, id ):

    def select_master_notification(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM alerts WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_master_notification( self, id ):

    def update_alert(self, data):
        # convert data types
        lst = list(data)
        if lst[0]:
            lst[0] = 1
        else:
            lst[0] = 0
        if lst[1]:
            lst[1] = 1
        else:
            lst[1] = 0
        if lst[2]:
            lst[2] = 1
        else:
            lst[2] = 0
        if lst[3]:
            lst[3] = 1
        else:
            lst[3] = 0
        data = tuple(lst)

        sql = 'UPDATE alerts SET syslog = ?, snmp = ?, email = ?, script = ? WHERE slave = ?;'
        cur = self.conn.cursor()
        cur.execute(sql, data)
    # end def update_state( self, data ):

    def select_state(self):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM state LIMIT 1')
        return cur.fetchone()
    # end def select_state( self, id ):

    def create_state(self):
        sql = 'INSERT INTO state(slave) VALUES(1);'
        cur = self.conn.cursor()
        cur.execute(sql)
        return cur.lastrowid
    # end def create_state( self, slave ):

    def update_state(self, data):
        sql = 'UPDATE state SET slave = ?;'
        cur = self.conn.cursor()
        cur.execute(sql, (data,))
    # end def update_state( self, data ):

    def close_con(self):
        self.conn.close()
        self.app.log.debug('Database connection closed')

    def create_role(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO roles(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_role( self, master, slave ):

    def select_role(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM roles WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_role( self, id ):

    def delete_role(self, master):
        sql = 'DELETE FROM roles WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_role( self, master ):

    def create_user(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO users(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_user( self, master, slave ):

    def select_user(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM users WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_user( self, id ):

    def delete_user(self, master):
        sql = 'DELETE FROM users WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_user( self, master ):

    def create_profile(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO profiles(master, slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_profile( self, master, slave ):

    def select_profile(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM profiles WHERE master=?', (id,))
        return cur.fetchone()
    # end def select_profile( self, id ):

    def delete_profile(self, master):
        sql = 'DELETE FROM profiles WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_profile( self, master ):

    def create_channel(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO channels(master, slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_channel( self, master, slave ):

    def select_channel(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM channels WHERE master=?', (id,))
        return cur.fetchone()
    # end def select_channel( self, id ):

    def delete_channel(self, master):
        sql = 'DELETE FROM channels WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_channel( self, master ):

    def create_bh(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO bhs(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_bh( self, master, slave ):

    def select_bh(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM bhs WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_bh( self, id ):

    def delete_bh(self, master):
        sql = 'DELETE FROM bhs WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_bh( self, master ):

    def create_blacklist(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO blacklists(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_blacklist( self, master, slave ):

    def select_blacklist(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM blacklists WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_blacklist( self, id ):

    def delete_blacklist(self, master):
        sql = 'DELETE FROM blacklists WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def ddelete_blacklistelete_bh( self, master ):

    def create_fmc_chapter(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO fmc_chapters(master, slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_fmc_chapter( self, master, slave ):

    def select_fmc_chapter(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM fmc_chapters WHERE master=?', (id,))
        return cur.fetchone()
    # end def select_fmc_chapter( self, id ):

    def delete_fmc_chapter(self, master):
        sql = 'DELETE FROM fmc_chapters WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_fmc_chapter( self, master ):

    def create_fmc_report(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO fmc_reports(master, slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_fmc_report( self, master, slave ):

    def select_fmc_report(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM fmc_reports WHERE master=?', (id,))
        return cur.fetchone()
    # end def select_fmc_report( self, id ):

    def delete_fmc_report(self, master):
        sql = 'DELETE FROM fmc_reports WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_fmc_report( self, master ):

    def create_fmc_email(self, data):
        # convert data types
        lst = list(data)
        if lst[2]:
            lst[2] = 1
        else:
            lst[2] = 0
        data = tuple(lst)

        sql = 'INSERT INTO fmc_emails(id,slave,active) VALUES(?,?,?,?,?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, data)
        return cur.lastrowid
    # end def create_fmc_email( self, data ):

    def delete_fmc_email(self, slave):
        sql = 'DELETE FROM fmc_emails WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (slave,))
    # end def delete_fmc_email( self, slave ):

    def select_fmc_email(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM fmc_emails WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_fmc_email( self, id ):

    def select_reporting(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM fmc_emails WHERE slave=?', (id,))
        return cur.fetchone()
    # end def select_reporting( self, id ):

    def select_master_reporting(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM fmc_emails WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_master_reporting( self, id ):

    def update_fmc_email(self, data):
        # convert data types
        lst = list(data)
        if lst[0]:
            lst[0] = 1
        else:
            lst[0] = 0
        data = tuple(lst)
        sql = 'UPDATE fmc_emails SET active = ? WHERE slave = ?;'
        cur = self.conn.cursor()
        cur.execute(sql, data)
    # end def update_fmc_email( self, data ):

    def create_fmc_alert(self, data):
        sql = 'INSERT INTO fmc_alerts(id,slave,syslog,snmp,email,script) VALUES(?,?,?,?,?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, data)
        return cur.lastrowid
    # end def create_fmc_alert( self, data ):

    def delete_fmc_alert(self, slave):
        sql = 'DELETE FROM fmc_alerts WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (slave,))
    # end def delete_fmc_alert( self, slave ):

    def select_fmc_alert(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM fmc_alerts WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_fmc_alert( self, id ):

    def select_alerting(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM fmc_alerts WHERE slave=?', (id,))
        return cur.fetchone()
    # end def select_notification( self, id ):

    def select_master_alerting(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM fmc_alerts WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_master_alerting( self, id ):

    def update_fmc_alert(self, data):
        sql = 'UPDATE fmc_alerts SET syslog = ?, snmp = ?, email = ?, script = ? WHERE slave = ?;'
        cur = self.conn.cursor()
        cur.execute(sql, data)
    # end def update_fmc_alert( self, data ):

    def create_custom_baseline(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO custom_baselines(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_custom_baseline( self, master, slave ):

    def select_custom_baseline(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM custom_baselines WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_custom_baseline( self, id ):

    def delete_custom_baseline(self, master):
        sql = 'DELETE FROM custom_baselines WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_custom_baseline( self, master ):

    def create_whitelist(self, master, slave):
        entry = (master, slave)
        sql = 'INSERT INTO whitelists(id,slave) VALUES(?,?);'
        cur = self.conn.cursor()
        cur.execute(sql, entry)
        return cur.lastrowid
    # end def create_whitelist( self, master, slave ):

    def select_whitelist(self, id):
        cur = self.conn.cursor()
        cur.execute('SELECT slave FROM whitelists WHERE id=?', (id,))
        return cur.fetchone()
    # end def select_whitelist( self, id ):

    def delete_whitelist(self, master):
        sql = 'DELETE FROM whitelists WHERE slave=?;'
        cur = self.conn.cursor()
        cur.execute(sql, (master,))
    # end def delete_whitelist( self, master ):
