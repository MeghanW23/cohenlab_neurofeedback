#!/bin/bash

scripts=(
"startup_docker.sh"
"aliases_and_functions.sh"
"get_ssh_keys.sh"
"make_venv.sh"
"tasks_run/scripts/RegisterFnirt.sh"
"tasks_run/scripts/TransferFilesE3.sh"
"tasks_run/scripts/PreprocRegisterE3.sh"
"tasks_run/scripts/CompareSettingsDifferences.sh")


for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        sudo chmod +x "$script"
    else
        echo "Warning: $script not found."
    fi
done