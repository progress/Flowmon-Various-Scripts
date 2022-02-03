#!/bin/bash
# @author Jiri Knapek <jiri.knapek@flowmon.com>
# This is an example script to use in Flowmon. It will take channels from
# profile All sources (live) and generate a graph for those. At this moment
# all with one collor
################################################################################
# start of mandatory part of source code

. /usr/local/bin/fmc_alert_functions
 
if [ -L $0 ] ; then
  DIR=$(dirname $(readlink -f $0)) ;
else
  DIR=$(dirname $0) ;
fi ;
 
input_json=$(cat "$DIR/pluginscript_input")
   
parse_alert_data "$input_json"

# end of mandatory part of source code

# Here we will list available channels in profile
PROFILE="live"
CHANNELS="$(ls /data/nfsen/profiles-data/$PROFILE/ | sed ':a;N;$!ba;s/\n/:/g')"

# This part is to get the top 10 output  of the profile and store it in /tmp/topstats.txt
/usr/local/bin/nfdump -M "/data/nfsen/profiles-data/$PROFILE/$CHANNELS" -r "${ALERT_TIMESLOT:0:4}/${ALERT_TIMESLOT:4:2}/${ALERT_TIMESLOT:6:2}/nfcapd.$ALERT_TIMESLOT" -n '10' -S 'srcport:p'/'bytes' -6 > /tmp/topstats.txt 

# Then we can also generate a graph to file /tmp/alarm.png
RRDS="$(ls /data/nfsen/profiles-stat/$PROFILE/*.rrd | grep -v npm)"
DEF=''
LINE1=''
for channel in $RRDS
do
   name=${channel##*/}
   name=$(echo "$name" | awk -F '.' '{print $1}')
   DEF="$DEF DEF:$name=$channel:traffic:AVERAGE"
   LINE1="$LINE1 LINE1:$name#0000FF:'$name'"
done

rrdtool graph /tmp/alarm.png -a PNG --end now --start end-120000s --width 400 --title="$PROFILE" $DEF $LINE1

# And how it's time to create a body for the email
printf "Hello, \n Alert $ALERT_NAME was triggered now. Top 10 souce ports are \n\n" > /tmp/body.txt
cat /tmp/topstats.txt >> /tmp/body.txt

# now we will send an emil to specified address
/usr/bin/php /var/www/shtml/index.php Cli:SendEmail -file="/tmp/body.txt" -to="jiri.knapek@flowmon.com" -attachments="/tmp/alarm.png" -subject="$ALERT_NAME"

# and cleant the tmp dir
rm /tmp/topstats.txt /tmp/body.txt /tmp/alarm.png
