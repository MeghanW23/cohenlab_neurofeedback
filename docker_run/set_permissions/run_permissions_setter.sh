#!/bin/bash
echo "Getting necessary paths now ..."
if [ -z "$permissions_script" ]; then 
    echo "Needed environment var: permissions_script is empty"
    exit 1
elif [ ! -f "$permissions_script" ]; then 
    echo "Path to permissions_script: ${permissions_script} was not found"
    exit 1
fi

if [ -z "$process_id_textfile" ]; then 
    echo "Needed environment var: process_id_textfile is empty"
    exit 1
elif [ ! -f "$process_id_textfile" ]; then 
    echo "Path to process_id_textfile: ${process_id_textfile} was not found"
    exit 1
fi

if [ -z "$nohup_log_file" ]; then 
    echo "Needed environment var: nohup_log_file is empty"
    exit 1
fi

if [ -z "$USER" ]; then 
    echo "Environment var: USER is empty"
    read -p "Press enter to continue without permission-setting. " continue_without_user
else
    echo "Current User is ${USER}"
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

sudo chmod 777 "$nohup_log_file"
if [ ! -f "$samba_ssh_priv_key" ]; then 
    echo "SSH Private key for Samba_User SSH: ${samba_ssh_priv_key} does not exist"
    echo "To make sshing into samba_user from your current user passwordless, do 'See Utility Tasks' and then 'Make SSH Keys for Passwordless SSH from current user to samba_user'"
    read -p "Press any key to continue without SSH Keys " 
fi

echo "SSH-ing into samba_user..."
ssh -i "$samba_ssh_priv_key" samba_user@localhost "WAIT_OR_START=${WAIT_OR_START} USER=${USER} ${permissions_script} > '$nohup_log_file' 2>&1 & disown"
sleep 5 # wait for process to start before getting process ID 

# Find the PID of the process using ps
permissions_script_basename=$(basename "$permissions_script")
permissions_script_basename_for_search="[${permissions_script_basename:0:1}]${permissions_script_basename:1}"
pid=$(ps aux | grep "$permissions_script_basename_for_search" | awk '{print $2}' | head -n 1)
if [ -z "$pid" ]; then
    echo "ERROR: Could not find process id after nohup call." 
    echo " " 
    echo "First 10 Lines of Log File:"
    echo " ----------------------- "
    head "$nohup_log_file"
    echo " ----------------------- "
    echo " " 
    echo "Last 10 Lines of Log File:"
    echo " ----------------------- "
    tail "$nohup_log_file"
    echo " ----------------------- "
    echo "Please look for errors in the Log File at: $nohup_log_file"
    read -p "Press enter to continue. " continue_without_permission
    exit 1
else
    # Save the PID to process_id.txt
    echo "$pid" > "$process_id_textfile"
    echo "Script started."
fi 