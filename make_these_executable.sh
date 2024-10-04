#!/bin/bash

dirpath="/workdir/tasks_run/scripts/"

# Read paths from the Python settings module, suppressing warnings
startup_docker_path=$(python3 -c "import sys; sys.path.append('$dirpath'); from settings import PATH_TO_STARTUP_SCRIPT; print(PATH_TO_STARTUP_SCRIPT)" 2>/dev/null)
aliases_and_functions=$(python3 -c "import sys; sys.path.append('$dirpath'); from settings import PATH_TO_ALIAS_SCRIPT; print(PATH_TO_ALIAS_SCRIPT)" 2>/dev/null)
get_ssh_keys=$(python3 -c "import sys; sys.path.append('$dirpath'); from settings import PATH_TO_SSH_MAKER; print(PATH_TO_SSH_MAKER)" 2>/dev/null)
make_venv=$(python3 -c "import sys; sys.path.append('$dirpath'); from settings import PATH_TO_VENV_MAKER; print(PATH_TO_VENV_MAKER)" 2>/dev/null)
RegisterFnirt=$(python3 -c "import sys; sys.path.append('$dirpath'); from settings import PATH_TO_FNIRT_REGISTRATION_SCRIPT; print(PATH_TO_FNIRT_REGISTRATION_SCRIPT)" 2>/dev/null)
TransferFilesE3=$(python3 -c "import sys; sys.path.append('$dirpath'); from settings import PATH_TO_TRANSFER_FILES_SCRIPT; print(PATH_TO_TRANSFER_FILES_SCRIPT)" 2>/dev/null)
PreprocRegisterE3=$(python3 -c "import sys; sys.path.append('$dirpath'); from settings import PATH_TO_E3_PREPROC_REGISTRATION_SCRIPT; print(PATH_TO_E3_PREPROC_REGISTRATION_SCRIPT)" 2>/dev/null)
CompareSettingsDifferences=$(python3 -c "import sys; sys.path.append('$dirpath'); from settings import PATH_TO_COMPARE_SETTINGS_SCRIPT; print(PATH_TO_COMPARE_SETTINGS_SCRIPT)" 2>/dev/null)

# Create an array with the actual paths
scripts=(
    "$startup_docker_path"
    "$aliases_and_functions"
    "$get_ssh_keys"
    "$make_venv"
    "$RegisterFnirt"
    "$TransferFilesE3"
    "$PreprocRegisterE3"
    "$CompareSettingsDifferences"
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
