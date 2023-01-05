#! /bin/bash

PLUGIN_NAME="Endace PtoV Comments"
MYPATH=`dirname $0`

. /usr/local/bin/common_functions

# Clear /etc/flowmon/pkg_versions.txt
cat /etc/flowmon/pkg_versions.txt | grep -v "$PLUGIN_NAME" > /tmp/pkg_versions.txt
move_file_safe /tmp/pkg_versions.txt /etc/flowmon/pkg_versions.txt

# Remove folder with the scripts
rm -rvf /data/components/endace

# Remove service directory
cd /
rm -rvf $MYPATH

# schmitez
exit 0