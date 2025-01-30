#!/bin/zsh

# open the vnc when a connection is made 
ip=$1
port=$2

# Set timeout limit in seconds (e.g., 10 min)
timeout_limit=600
timeout_counter=0

# if the log doesn't exist, trigger the vnc viewer pop-up when it's created
if [ ! -f vnc_trigger.log ]; then
    while true; do
        if [ -f vnc_trigger.log ]; then
            /Applications/TigerVNC\ Viewer\ 1.14.1.app/Contents/MacOS/TigerVNC\ Viewer ${ip}:${port} > /dev/null 2>&1 && exit
            exit
        fi
        sleep 0.1
        timeout_counter=$((timeout_counter + 1))
        if [ "$timeout_counter" -ge "$timeout_limit" ]; then
            echo "OPEN VNC VIEWER SCRIPT: Timeout reached, exiting."
            exit 1
        fi
    done
fi

# if the log does exist, trigger the vnc viewer pop-up when there is a new line in the viewer
starting_line_count=$(cat vnc_trigger.log | wc -l)
while true; do
    current_line_count=$(cat vnc_trigger.log | wc -l)
    if [ "$current_line_count" != "$starting_line_count" ]; then 
        /Applications/TigerVNC\ Viewer\ 1.14.1.app/Contents/MacOS/TigerVNC\ Viewer ${ip}:${port} > /dev/null 2>&1 && exit
        exit
    fi
    sleep 0.1
    timeout_counter=$((timeout_counter + 1))
    if [ "$timeout_counter" -ge "$timeout_limit" ]; then
        echo "OPEN VNC VIEWER SCRIPT: Timeout reached, exiting."
        exit 1
    fi
done
