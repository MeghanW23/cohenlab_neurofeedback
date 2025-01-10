#!/bin/zsh

# open the vnc when a connection is made 
ip=$1
port=$2
while true; do
    nc -zv "$ip" "$port" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        # /Applications/TigerVNC\ Viewer\ 1.14.1.app/Contents/MacOS/TigerVNC\ Viewer ${ip}:${port} > /dev/null 2>&1
        open vnc://localhost:5999
        exit
    fi
    sleep 0.1
done
