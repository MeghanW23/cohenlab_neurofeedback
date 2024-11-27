#!/bin/bash

echo "Running the permissions setting script now..." 

# Start the permissions-setting process in the background with nohup
nohup sudo -u "samba_user" bash -c "/Users/meghan/cohenlab_neurofeedback/docker_run/set_permissions/setpermissions.sh" > nohup.out 2>&1 &

# Give the background process a moment to start (just in case)
sleep 1

# Find the PID of the process using ps, avoiding the grep command
pid=$(ps aux | grep "[s]etpermissions.sh" | awk '{print $2}' | head -n 1)

# Save the PID to process_id.txt
echo "$pid" > process_id.txt

echo "Script started."