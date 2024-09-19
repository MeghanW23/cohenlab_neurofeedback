#!/bin/bash

# Variables needed
user_file="/workdir/users.txt"

# Setup Aliases
echo "alias rifg='python /workdir/tasks_run/scripts/rifg_task.py'" >> ~/.bashrc
echo "alias data='cd /workdir/tasks_run/data/'" >> ~/.bashrc
echo "alias logs='cd /workdir/tasks_run/data/logs'" >> ~/.bashrc
echo "alias scripts='cd /workdir/tasks_run/scripts'" >> ~/.bashrc
echo "alias samba='cd /workdir/tasks_run/data/sambashare'" >> ~/.bashrc
echo "alias mock='python /workdir/tasks_run/scripts/other/mock_mri_file_production.py'" >> ~/.bashrc
echo "alias nfb='python /workdir/tasks_run/scripts/nf_calc_MW.py'" >> ~/.bashrc
echo "alias msit='python /workdir/tasks_run/scripts/MSIT_NF_latest.py'" >> ~/.bashrc
echo "alias testdir='cd /workdir/tasks_run/data/sambashare/test_dir'" >> ~/.bashrc
echo "alias clear_testdir='rm -rf /workdir/tasks_run/data/sambashare/test_dir/*'" >> ~/.bashrc
echo "e3() {
cd /workdir/
./ssh_e3.sh
}" >> ~/.bashrc

# Get CH ID
CHID=$(grep "^$USERNAME," "$user_file" | awk -F', ' '{print $2}')

# Use single quotes to prevent immediate expansion
echo "export CHID='${CHID}'" >> ~/.bashrc

# Source the .bashrc file to apply changes
source ~/.bashrc

# setup passwordless ssh if not dont already
./get_ssh_keys

# Display to User
if [ -n "$USERNAME" ]; then
    echo "Hello, $USERNAME. Docker container setup is all set. Type 'alias' to see available commands."
else
    echo "Docker container setup is all set. Type 'alias' to see available commands."
fi

# Execute any commands passed to the script
exec "$@"
