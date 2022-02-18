# False-positive cleanup

This script can delete all false positive rules configured which has not been used since a time specified by paramere or all which has not been used at all.

You must use before option with date in ISO format the others are optional. It is supposed to be run on python3.6 as I use it on Flowmon but it requires additional Python modules which are not present by default.

- requests (for flowmon python36-requests-2.14.2-2.el7.noarch.rpm) and it's dependencies
  - chardet (python36-chardet-3.0.4-1.el7.noarch.rpm)
  - idna (python36-idna-2.7-2.el7.noarch.rpm)
  - urllib3 (python36-urllib3-1.25.6-1.el7.noarch.rpm)
   - six (python36-six-1.14.0-2.el7.noarch.rpm)
   - pysocks (python36-pysocks-1.6.8-7.el7.noarch.rpm)

The easiest would be so to run this from a different machine and modify the script to use that location by changing BASE_URL

It might not delete everything on Flowmon ADS less then 12 as there were some issues with the endpoint to delete false positive rule.

```
usage: fpcleanup.py <options>

Mandatory:
    --before YYYY-MM-DD    Date in format YYYY-MM-DD (i.e., 2022-02-18). This is time which would be used
                           as the oldest when the false-positive was used the last time

Optional:
    --empty yes            Delete also these not used since creation
    --user <username>      Username used for the authentication to Flowmon appliance
    --pass <password>      Password for the user authentication
```