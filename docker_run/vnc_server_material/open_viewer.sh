#!/bin/bash

settings_script_path="$1"
port="$2"

timeout_duration=600  # Timeout in seconds

# Check if settings_script_path is provided
if [ -z "$settings_script_path" ]; then 
    echo "ERROR: no settings_script_path specified" 
    exit 1
fi 

# Check if port is provided
if [ -z "$port" ]; then 
    echo "ERROR: no port specified" 
    exit 1
fi 

# Get OPEN_VIEWER_LOG path from Python script
OPEN_VIEWER_LOG="$(python "$settings_script_path" OPEN_VIEWER_LOG -s)" 

# Check if the file exists
if [ ! -f "$OPEN_VIEWER_LOG" ]; then 
    echo "Waiting for new file..."
    
    start_time=$(date +%s)  # Capture the start time

    while true; do  
        current_time=$(date +%s)
        elapsed_time=$((current_time - start_time))

        # Exit the loop if timeout is reached
        if [ $elapsed_time -ge $timeout_duration ]; then
            echo "ERROR: Timeout reached, file did not appear within ${timeout_duration} seconds."
            exit 1
        fi

        if [ -f "$OPEN_VIEWER_LOG" ]; then 
            echo "Opening vncviewer"
            vncviewer localhost:${port}
            exit 
        else 
            echo "Waiting for new file..."
            sleep 0.1 
        fi
    done 
else
    starting_lines_in_log="$(cat "$OPEN_VIEWER_LOG" | wc -l)"
    start_time=$(date +%s)  # Capture the start time

    while true; do  
        current_lines_in_log="$(cat "$OPEN_VIEWER_LOG" | wc -l)"
        current_time=$(date +%s)
        elapsed_time=$((current_time - start_time))

        # Exit the loop if timeout is reached
        if [ $elapsed_time -ge $timeout_duration ]; then
            echo "ERROR: Timeout reached, no change in log file within ${timeout_duration} seconds."
            exit 1
        fi

        if [ "$current_lines_in_log" != "$starting_lines_in_log" ]; then 
            echo "Opening vncviewer"
            vncviewer localhost:${port}
            exit 
        else 
            echo "Waiting for new line..."
            sleep 0.1 
        fi
    done 
fi
