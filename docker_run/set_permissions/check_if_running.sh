#!/bin/bash
set -e 

function run_permissions_setter {

}

log_path="/Users/meghan/cohenlab_neurofeedback/docker_run/set_permissions/nohup.out"
pid_txt_file="/Users/meghan/cohenlab_neurofeedback/docker_run/set_permissions/process_id.txt"
pid=$(cat "$pid_txt_file")
if [ ! -f "$pid_txt_file" ]; then 
    echo "Could not find PID text file "
fi

if [ ! -f "$log_path" ]; then 
    echo "Permissions-Setting Script is not Actively Running."
    run_permissions_setter "$log_path"
else
if ps -p $pid > /dev/null; then
    echo "Process $pid is running."
else
    echo "Process $pid is not running."
fi
    
fi 

