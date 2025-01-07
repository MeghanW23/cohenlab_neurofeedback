#!/bin/zsh

# open the vnc when a connection is made 
ip=$1
port=$2
while true; do
    nc -zv "$ip" "$port" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        open vnc://"$ip":"$port"
        exit
    fi
    sleep 0.1
done
