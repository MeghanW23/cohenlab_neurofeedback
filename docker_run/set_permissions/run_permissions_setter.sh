#!/bin/bash
echo "Getting necessary paths now ..."
if [ -z "$permissions_script" ]; then 
    echo "Needed environment var: permissions_script is empty"
    read -p "Press enter to continue without permission-setting. " continue_without_permission
    exit 1
elif [ ! -f "$permissions_script" ]; then 
    echo "Path to permissions_script: ${permissions_script} was not found"
fi

if [ -z "$process_id_textfile" ]; then 
    echo "Needed environment var: process_id_textfile is empty"
    read -p "Press enter to continue without permission-setting. " continue_without_permission
    exit 1
elif [ ! -f "$process_id_textfile" ]; then 
    echo "Path to permissions_script: ${process_id_textfile} was not found"
fi

if [ -z "$nohup_log_file" ]; then 
    echo "Needed environment var: nohup_log_file is empty"
    read -p "Press enter to continue without permission-setting. " continue_without_permission
    exit 1
fi

echo "Would you like to set permissions for a currently running directory or wait for a new directory?"
while true; do 
    read -p "Type 'wait' to wait for a new directory. Type 'start' to start immediately: " WAIT_OR_START
    if [ "$WAIT_OR_START" = "start" ]; then 
        echo "Ok, the permissions-setting script will start immediately."
        break
    elif [ "$WAIT_OR_START" = "wait" ]; then
        echo "Ok, the permissions-setting script will wait for a new directory."
        break
    else
        echo "Please type either 'wait' or 'start'. Try again."
    fi
done


# Start the permissions-setting process in the background with nohup
echo "Changing nohup.log permissions..."
touch "$nohup_log_file"

echo "If prompted, please enter your samba_user password. Else, you are all set ..." 
sudo chmod 777 "$nohup_log_file"
sudo -u "samba_user" bash -c "sudo WAIT_OR_START=${WAIT_OR_START} ${permissions_script} > '$nohup_log_file' 2>&1 & disown"

sleep 10 # wait for process to start before getting process ID 

# Find the PID of the process using ps
permissions_script_basename=$(basename "$permissions_script")
permissions_script_basename_for_search="[${permissions_script_basename:0:1}]${permissions_script_basename:1}"
pid=$(ps aux | grep "$permissions_script_basename_for_search" | awk '{print $2}' | head -n 1)
if [ -z "$pid" ]; then
    echo "Could not find process id after nohup call." 
    echo "Please look for errors. "
    read -p "Press enter to continue without permission-setting. " continue_without_permission
    exit 1
else
    # Save the PID to process_id.txt
    echo "$pid" > "$process_id_textfile"
    echo "Script started."
fi 