#!/bin/bash

user_file="/workdir/users.txt"

# Setup starting aliases
echo "Setting up aliases ..."
echo "alias commands='alias && declare -f'" >> ~/.bashrc
echo "alias rifg='python /workdir/tasks_run/scripts/rifg_task.py'" >> ~/.bashrc
echo "alias data='cd /workdir/tasks_run/data/'" >> ~/.bashrc
echo "alias logs='cd /workdir/tasks_run/data/logs'" >> ~/.bashrc
echo "alias scripts='cd /workdir/tasks_run/scripts'" >> ~/.bashrc
echo "alias samba='cd /workdir/tasks_run/data/sambashare'" >> ~/.bashrc
echo "alias mock='python /workdir/tasks_run/scripts/other/mock_mri_file_production.py'" >> ~/.bashrc
echo "alias nfb='python /workdir/tasks_run/scripts/nf_calc_MW.py'" >> ~/.bashrc
echo "alias premsit='python /workdir/tasks_run/scripts/MSIT_NF_PRE.py'" >> ~/.bashrc
echo "alias postmsit='python /workdir/tasks_run/scripts/MSIT_NF_POST.py'" >> ~/.bashrc
echo "alias testdir='cd /workdir/tasks_run/data/sambashare/test_dir'" >> ~/.bashrc
echo "alias cleartestdir='rm -rf /workdir/tasks_run/data/sambashare/test_dir/*'" >> ~/.bashrc
echo "alias venv='source /workdir/venv/bin/activate'" >> ~/.bashrc
echo "alias localize='python /workdir/tasks_run/scripts/Localizer.py'" >> ~/.bashrc
echo "alias cleandocker='python /workdir/tasks_run/scripts/ClearDirs.py'" >> ~/.bashrc
echo "alias e3transfer='return_here=\$(pwd) && cd /workdir/tasks_run/scripts && ./TransferFilesE3.sh \"\$@\" && cd \"\$return_here\"'" >> ~/.bashrc
echo "Aliases Set."

# Get CH ID from users file
echo "Getting CHID ..."
CHID=$(grep "^$USERNAME," "$user_file" | awk -F', ' '{print $2}')
# set user's chid as an environment ent
echo "export CHID='${CHID}'" >> ~/.bashrc
echo "Got CHID: $CHID"

source ~/.bashrc # update before using environmental variable to make ssh keys if needed

# Check if SSH key already exists, if not- create ssh keys based on ch id inputted during docker image creation
echo "Checking for SSH keys ..."
if [ ! -f "/workdir/.ssh/docker_e3_key_$CHID" ]; then
  echo "No SSH Key Detected."
  ./get_ssh_keys.sh
else
  echo "SSH keys found successfully."
fi

# setup passwordless ssh alias
echo "alias e3='ssh -F /workdir/.ssh/config_${CHID} e3_${CHID}'" >> ~/.bashrc

echo "Checking for the existence of the Python virtual environment ..."
if [ ! -d "venv/" ]; then
  while true; do
    read -p "Python virtual environment not found. Create the virtual env? (y/n) " create_choice
    if [ "$create_choice" = 'y' ]; then
      echo "Ok, creating virtual environment now ..."
      ./make_venv.sh
      break
    else
      echo "Ok, I won't create the virtual environment. You can create it later by running the script: ./make_venv.sh"
      break
    fi
  done
else
  echo "Found Python virtual environment successfully."
fi

# Display to User
echo -e "\e[1;32m\n╔═════════════════════════════════════════════╗"
echo -e "\e[1;32m  🚀 Neurofeedback Docker Container Built 🚀  "
echo -e "\e[1;32m╚═════════════════════════════════════════════╝\e[0m"

if [ -n "$USERNAME" ]; then
    # echo "Hello, . Docker container setup is all set. Type 'commands' to see available commands."
  echo -e "\e[1;33m\nHello, ${USERNAME}. Docker container setup is complete. \n  ⚙️  To list useful commands, type 'commands'. \n  🐍 Type 'venv' to activate the python environment.\n \e[0m"


else
  echo -e "\e[1;33mHello. Docker container is complete. \n  ⚙️️  To list useful commands, type 'commands'.  \n  🐍 Type 'venv' to activate the python environment.\n  \e[0m"


fi

# Source the .bashrc file to apply changes
source ~/.bashrc

# Execute any commands passed to the script
exec "$@"
