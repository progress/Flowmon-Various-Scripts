#!/bin/bash

# set -x
# start of mandatory part of source code
. /usr/libexec/fmc_alert_functions

input_json="$1"
parse_alert_data "$input_json"
# end of mandatory part of source code

# Get script parameters
# First argument is the alert JSON passed by Flowmon internals.
# Shift it away so getopts parses only user options (-p, -m).
shift

PROFILE=""
MAIL=""

while getopts ":p:m:" opt; do
    case "${opt}" in
        p)
            PROFILE=${OPTARG}
            ;;
        m)
            MAIL=${OPTARG}
            ;;
        :)
            echo "Missing value for option: -${OPTARG}" >&2
            echo "Usage: cmd -p <profile_name> -m <mail address>" >&2
            exit 1
            ;;
        \?)
            echo "Unknown option: -${OPTARG}" >&2
            echo "Usage: cmd -p <profile_name> -m <mail address>" >&2
            exit 1
            ;;
    esac
done

echo "DEBUG: input_json='${input_json}' PROFILE='${PROFILE}' MAIL='${MAIL}'" >&2

if [ -z "$PROFILE" ] || [ -z "$MAIL" ]; then
    echo "Usage: cmd -p <profile_name> -m <mail address>" >&2
    exit 1
fi

# List available channels in profile
# PROFILE="All Sources"

php /var/www/shtml/index.php Cli:GetConfigurationXML -section='cfg_fmc_profiles' > /tmp/profiles.xml

# Extract channel IDs for the profile from profiles.xml
PROFILES_XML="/tmp/profiles.xml"

# Use xmllint to extract all <id> values from the profile matching PROFILE name
CHANNELS=$(xmllint --xpath "//profile[name='$PROFILE']//id/text()" "$PROFILES_XML" 2>/dev/null | tr '\n' ' ' | sed 's/ *$//')

# Conversion to UTC (start)
START_UTC=$(date -u -d "$ALERT_TIMESLOT" +"%Y/%m/%d.%H:%M:%S")

# +5 minutes (end)
END_UTC=$(date -u -d "$ALERT_TIMESLOT +5 minutes" +"%Y/%m/%d.%H:%M:%S")

# Create a range for the nfdump command
RANGE="${START_UTC}-${END_UTC}"

# Query the top 10 source IP addresses from the Flowmon database and save it to a temporary file
/data/components/flowsen/bin/nfdump -C $CHANNELS -t "$RANGE" -T -S 'srcip'/'fl' -n '10' --time-precision msec > /tmp/topstats.txt 

# Create a body for the email
printf "Hello, \n Alert $ALERT_NAME was triggered now. Top 10 source IP addresses are \n\n" > /tmp/body.txt
# printf "Executed command:\n/data/components/flowsen/bin/nfdump -C \"$CHANNELS\" -t \"$RANGE\" -T -S 'srcip'/'fl' -n '10' --time-precision msec\n\n" >> /tmp/body.txt
cat /tmp/topstats.txt >> /tmp/body.txt

# Send an e-mail to specified address
/usr/bin/php /var/www/shtml/index.php Cli:SendEmail -file="/tmp/body.txt" -to="$MAIL" -subject="$ALERT_NAME"

# Clean the tmp dir
rm /tmp/topstats.txt /tmp/body.txt /tmp/profiles.xml