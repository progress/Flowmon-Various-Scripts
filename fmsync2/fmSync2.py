#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
The purpose of this application is to synchronization using Flowmon API
=========================================================================================
"""
__author__ = "Jiri Knapek"
__copyright__ = "Copyright 2021, Flowmon Networks"
__credits__ = ["Jiri Knapek"]
__license__ = "GPL"
__version__ = "3.0"
__maintainer__ = "Jiri Knapek"
__email__ = "jiri.knapek@flowmon.com"
__status__ = "beta"

from cli.restcli import restcli

# Main method to run the application
def main():
    # start cement app with configuration
    with restcli() as app:
        app.run()
        app.log.info('Completed')

if __name__ == '__main__':
    # execute only if runs as a script
    main()