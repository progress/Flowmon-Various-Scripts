#!/bin/bash

# Author: Tonny van der Cammen
# Description: This script sends Telegram messages for ADS events



function usage {
    cat << EOF >&2
usage: telegram.sh <options>

Required:
    --chat_id      chat_id for your telegram BOT
    --API-Key       api key for your telegram account
   
    
EOF
    exit
}      

params="$(getopt -o f:u:h -l chat_id:,API-Key:,help --name "telegram.sh" -- "$@")"

if [ $? -ne 0 ]
then
    usage
fi

eval set -- "$params"
unset params

while true
do
    case $1 in
        -f|--chat_id)
            ChatID=("${2-}")
            shift 2
            ;;
        -u|--API-Key)
            TOKEN=("${2-}")
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        --)
            shift
            break
            ;;
        *)
            usage
            ;;
    esac
done

# we dont support any other args
[ $# -gt 0 ] && {
    usage
}

cat << EOF >&2
-----  My params are ------------------
ChatID = $ChatID
TOKEN = $TOKEN

---------------------------------------
EOF

echo "Stdin read started..." >&2

LINE_NUM=1
array=()
while read line
do
    IFS=$'\t'
    array=($line)
   

 MESSAGE="There is a ${array[6]} event detected with ID ${array[0]}. At ${array[1]} on Source IP ${array[10]} With Destination IP ${array[12]}.  Method used ${array[4]} with result ${array[7]}"


     
    LINE_NUM=$((LINE_NUM+1))

	
    # send message
	

	
	curl -s -X POST https://api.telegram.org/bot$TOKEN/sendMessage -d chat_id=$ChatID -d text="$MESSAGE"
	
    



done < /dev/stdin

echo "---- Everything completed ----"





