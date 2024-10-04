#!/bin/bash

dirpath="/workdir/tasks_run/scripts/"

# Read paths from the Python settings module
startup_docker_path=$(python3 -c "import sys; sys.path.append('$dirpath'); from settings import PATH_TO_STARTUP_SCRIPT; print(PATH_TO_STARTUP_SCRIPT)")
aliases_and_functions=$(python3 -c "import sys; sys.path.append('$dirpath'); from settings import PATH_TO_ALIAS_SCRIPT; print(PATH_TO_ALIAS_SCRIPT)")
get_ssh_keys=$(python3 -c "import sys; sys.path.append('$dirpath'); from settings import PATH_TO_SSH_MAKER; print(PATH_TO_SSH_MAKER)")
make_venv=$(python3 -c "import sys; sys.path.append('$dirpath'); from settings import PATH_TO_VENV_MAKER; print(PATH_TO_VENV_MAKER)")
RegisterFnirt=$(python3 -c "import sys; sys.path.append('$dirpath'); from settings import PATH_TO_FNIRT_REGISTRATION_SCRIPT; print(PATH_TO_FNIRT_REGISTRATION_SCRIPT)")
TransferFilesE3=$(python3 -c "import sys; sys.path.append('$dirpath'); from settings import PATH_TO_TRANSFER_FILES_SCRIPT; print(PATH_TO_TRANSFER_FILES_SCRIPT)")
PreprocRegisterE3=$(python3 -c "import sys; sys.path.append('$dirpath'); from settings import PATH_TO_E3_PREPROC_REGISTRATION_SCRIPT; print(PATH_TO_E3_PREPROC_REGISTRATION_SCRIPT)")
CompareSettingsDifferences=$(python3 -c "import sys; sys.path.append('$dirpath'); from settings import PATH_TO_COMPARE_SETTINGS_SCRIPT; print(PATH_TO_COMPARE_SETTINGS_SCRIPT)")

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
        sudo chmod +x "$script"
        echo "Made $script executable."
    else
        echo "Warning: $script not found."
    fi
done
