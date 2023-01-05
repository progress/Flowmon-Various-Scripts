#! /bin/bash

PLUGIN_NAME="Endace PtoV Comments"
PLUGIN_VERSION=`cat /tmp/flowmon-update/version.txt | sed 's/^.*;//'`
NEWVER=$(echo $PLUGIN_VERSION | tr -d '.')
CURVER=`cat /etc/flowmon/pkg_versions.txt | grep "$PLUGIN_NAME" | cut -d ';' -f 2 | tr -d '.'` # currently installed version
DATADIR="/tmp/flowmon-update/data"


if [ -z $CURVER ]; then
    CURVER=0
fi


. /usr/local/bin/common_functions
if [ -z $COMM_FUNC_VERSION ]; then
    COMM_FUNC_VERSION=0
fi

# update plugin version
sed -i '/^'"$PLUGIN_NAME"';/d' /etc/flowmon/pkg_versions.txt
# remove previous package name
sed -i '/^'"$PLUGIN_NAME"'/d' /etc/flowmon/pkg_versions.txt
echo "$PLUGIN_NAME;$PLUGIN_VERSION" >> /etc/flowmon/pkg_versions.txt
