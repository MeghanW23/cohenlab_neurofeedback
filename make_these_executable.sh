#!/bin/bash

dirpath="/workdir/tasks_run/scripts/"

# Create an array with the actual paths
scripts=(
    "$PATH_TO_STARTUP_SCRIPT"
    "$PATH_TO_ALIAS_SCRIPT"
    "$PATH_TO_SSH_MAKER"
    "$PATH_TO_VENV_MAKER"
    "$PATH_TO_FNIRT_REGISTRATION_SCRIPT"
    "$PATH_TO_TRANSFER_FILES_SCRIPT"
    "$PATH_TO_E3_PREPROC_REGISTRATION_SCRIPT"
    "$PATH_TO_COMPARE_SETTINGS_SCRIPT"
)

# Iterate through the scripts array and change permissions
for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        # Check if the script is already executable
        if [ ! -x "$script" ]; then
            echo "Making $script executable..."
            sudo chmod +x "$script"
        else
            echo "$script is already executable."
        fi
    else
        echo "Warning: $script not found."
    fi
done
