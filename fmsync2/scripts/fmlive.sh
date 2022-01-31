#! /bin/bash

/usr/bin/python3 /data/components/fmsync2/scripts/fmSync2.py getstate
STATE=$?
/usr/bin/python3 /data/components/fmsync2/scripts/fmSync2.py livecheck
if [ $? -gt 0 ]
then
	if [ $STATE -eq 0 ]
	then
		/usr/bin/python3 /data/components/fmsync2/scripts/fmSync2.py master
	fi
else
	if [ $STATE -gt 0 ]
	then
		/usr/bin/python3 /data/components/fmsync2/scripts/fmSync2.py slave
	fi
fi