This script now implements API for DDD, FOS and ADS, to synchronize all required configuration.

Its purpose is to have two Flowmon collectors works as a pair with sort of HA. It is expected to be deployed only on a single appliance working as backup and thus not sending any email alerts. Once you want you can switch it manually or automatically with a script to start also sending the notifications.

You won't be able to use it as it is since it has some requirements and needs to be installed as root user, but it could be a good inspiration as a complex REST API work with Flowmon appliance.


## DDD supports
- sync all configuration items
- keep persistent information about IDs
- configurable functions (active/active or active/passive for script mitigation)
- live check to switch itself to master

## FOS
- roles - for FOS 10.3.x
- users - for FOS 10.3.x
- profiles
- business hours
- blacklists
- chapters
- reports
- email reports
- alerts

## ADS
- data feeds
- filters
- perspectives
- methods and their instances (with exception of custom blacklist as they cannot be synced now)
- email event reporting

It requires on Flowmon OS these additional packages for Python 3 (in the brackets are used in my package)
- Cement CLI Application Framework for Python version 2.10.12 (cement-2.10.12-py3-none-any.whl)
- PySocks (python36-pysocks-1.6.8-7.el7.noarch.rpm)
- Requests (python36-requests-2.14.2-2.el7.noarch.rpm)
- Six (python36-six-1.14.0-2.el7.noarch.rpm)
- urllib3 (python36-urllib3-1.25.6-1.el7.noarch.rpm)
- idna (python36-idna-2.7-2.el7.noarch.rpm)
