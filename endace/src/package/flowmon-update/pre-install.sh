#! /bin/bash

PLUGIN_VER=`cat /tmp/flowmon-update/version.txt | sed 's/^.*;//'`
NEWVER=`echo $PLUGIN_VER|sed 's/\.//'g`  # new version to be installed
DATADIR="/tmp/flowmon-update/data"
SERVDIR="/etc/flowmon/plugins/endace"
PLUGIN_NAME="Endace PtoV Comments"

OSV=`uname -i`
CURVER=`cat /etc/flowmon/pkg_versions.txt | grep "$PLUGIN_NAME" | cut -d ';' -f 2 | tr -d '.'` # currently installed version

if [ -z $CURVER ]; then
    CURVER=0
fi

PROBE_VERSION=`cat /etc/flowmon/pkg_versions.txt | grep "FlowMon Probe" | cut -d ';' -f 2 | tr -d '.'`
COLL_VERSION=`cat /etc/flowmon/pkg_versions.txt | grep "FlowMon Collector" | cut -d ';' -f 2 | tr -d '.'`

if [ -z $PROBE_VERSION ]; then
    VERS=$COLL_VERSION
elif [ -z $COLL_VERSION ]; then
    VERS=$PROBE_VERSION
fi

if [ -z $VERS ]; then
    VERS=0
fi

if [ $VERS -lt 100309 ]; then
    echo "This version can be installed on Flowmon device 10.3.9 and newer!" > /tmp/flowmon-update.err
    exit 10
fi

. /usr/local/bin/common_functions

SUDOUSER="ADMINS"

if [ $CURVER -lt $NEWVER ]; then
    if [ $CURVER -eq 0 ]; then
        # fresh install
        # create service directory and copy uninstall script there
        mkdir -p $SERVDIR
        install -m 755 /tmp/flowmon-update/data/uninstall.sh $SERVDIR
        chown root:root $SERVDIR/uninstall.sh
        cat <<EOF > $SERVDIR/plugin.cfg
name=$PLUGIN_NAME
status=stopped
EOF
        # create directory and copy everything for the scripts
        mkdir -v /data/components/endace
        mkdir -v /data/components/endace/etc
        mkdir -v /data/components/endace/log
        cp -vr $DATADIR/* /data/components/endace/
        chown -vR flowmon:flowmon /data/components/endace
        chmod -v 755 /data/components/endace/add-comment.py
        rm -vf /data/components/endace/uninstall.sh

    fi
else
    echo "This version of Endace PtoV Comments is already installed!" > /tmp/flowmon-update.err
    exit 10
fi
