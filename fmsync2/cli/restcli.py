from core.main import main
from cement.core.foundation import CementApp
from cement.core.controller import CementBaseController, expose
from cement.core import backend
import sys

# define CLI controller


class cliBase(CementBaseController):
    class Meta:
        label = 'base'
        description = "The purpose of this application is to synchronization using Flowmon API."
        epilog = "It is curently in beta testing phase"

    @expose(hide=True, aliases=['run'])
    def default(self):
        self.app.log.info(
            'No action specified. Check -h if you need some assitance')

    @expose(help="Sync with the master configuration")
    def sync(self):
        self.app.log.info('Running full synchronization now...')
        control = main(self.app)
        if control.sync():
            sys.exit(0)
        else:
            sys.exit(1)

    @expose(help="Manual persistent state DB init")
    def init(self):
        self.app.log.info('Running database init...')
        control = main(self.app)
        control.init()

    @expose(help="First sync with the master configuration to fill the persistent DB")
    def first(self):
        self.app.log.info('Running first sync to initialize persistent DB')
        control = main(self.app)
        control.sync(True)

    @expose(help="Set the slave on this unit")
    def slave(self):
        self.app.log.info('Setting this box as a slave')
        control = main(self.app)
        control.set_state(1)

    @expose(help="Set the master on this unit")
    def master(self):
        self.app.log.info('Setting this box as a master')
        control = main(self.app)
        control.set_state(0)

    @expose(help="Perform the live check")
    def livecheck(self):
        self.app.log.info('Checking connections')
        control = main(self.app)
        value = control.live_check()
        if value:
            sys.exit(0)
        else:
            sys.exit(1)

    @expose(help="Get local state information")
    def getstate(self):
        self.app.log.info('Checking current state')
        control = main(self.app)
        value = control.get_state()
        if value:
            sys.exit(1)
        else:
            sys.exit(0)


class restcli(CementApp):
    class Meta:
        label = 'fmsync'
        base_controller = cliBase
        config_files = ['/data/components/fmsync2/etc/config.ini']
