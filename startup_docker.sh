#!/bin/bash

# Variables needed
user_file="/workdir/users.txt"

# Setup starting aliases
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
echo "alias venv='source /workdir/venv/bin/activate'" >> ~/.bashrc
echo "e3transfer() {
  return_here=\$(pwd)
  cd /workdir/tasks_run/scripts
  ./TransferFilesE3.sh \"\$@\"
  cd \"\$return_here\"
}" >> ~/.bashrc

# Get CH ID from users file
CHID=$(grep "^$USERNAME," "$user_file" | awk -F', ' '{print $2}')

# set user's chid as an environment ent
echo "export CHID='${CHID}'" >> ~/.bashrc
echo "Your CHID is: ${CHID}"

source ~/.bashrc # update before using environmental variable to make ssh keys if needed

# Check if SSH key already exists, if not- create ssh keys based on ch id inputted during docker image creation
if [ ! -f "/workdir/.ssh/docker_e3_key_$CHID" ]; then
  echo "No SSH Key Detected."
  ./get_ssh_keys.sh
fi

# setup passwordless ssh alias
echo "alias e3='ssh -F /workdir/.ssh/config_${CHID} e3_${CHID}'" >> ~/.bashrc


# Display to User
if [ -n "$USERNAME" ]; then
    echo "Hello, $USERNAME. Docker container setup is all set. Type 'alias' to see available commands."
else
    echo "Docker container setup is all set. Type 'alias' to see available commands."
fi

# Source the .bashrc file to apply changes
source ~/.bashrc

# Execute any commands passed to the script
exec "$@"
