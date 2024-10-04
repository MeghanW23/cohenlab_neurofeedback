#!/bin/bash

# end if error
set -e

# Get CH ID from users file (should have been added during docker image build)
echo "Getting CHID ..."
user_file="/workdir/users.txt"
CHID=$(grep "^$USERNAME," "$user_file" | awk -F', ' '{print $2}')
echo "export CHID='${CHID}'" >> ~/.bashrc # set user's chid as an environment env
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

echo "Setting correct permissions for the e3 private key"
chmod 600 /workdir/.ssh/docker_e3_key_"$CHID"
echo "Permissions set."

# set up runtime aliases and functions
echo "Setting up aliases ..."
source aliases_and_functions.sh # source to have it run in the current shell and have access to the environment variables
echo "Aliases Set."

# create python virtual environment, if it doesnt already exist
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

# Append the necessary FSL environmental variables to .bashrc
echo "Exporting FSL Path Environment Variables ..."
echo "export FSLDIR=/usr/local/fsl" >> /root/.bashrc
echo "export PATH=\$FSLDIR/bin:\$PATH" >> /root/.bashrc
echo "export USER=$(whoami)" >> /root/.bashrc
echo ". \$FSLDIR/etc/fslconf/fsl.sh" >> /root/.bashrc

echo "Make the scripts executable ..."
sudo chmod +x /workdir/make_these_executable.sh
/workdir/make_these_executable.sh && echo "All set." || echo "Error Making Scripts Executable"

# Display to User
echo -e "\e[1;32m\n╔═════════════════════════════════════════════╗"
echo -e "\e[1;32m  🚀 Neurofeedback Docker Container Created 🚀  "
echo -e "\e[1;32m╚═════════════════════════════════════════════╝\e[0m"

if [ -n "$USERNAME" ]; then
    # echo "Hello, . Docker container setup is all set. Type 'commands' to see available commands."
  echo -e "\e[1;33m\nHello, ${USERNAME}. Docker container setup is complete. \n  🔧  To list useful commands, type 'commands'. \n\e[0m"
else
  echo -e "\e[1;33mHello. Docker container is complete. \n  🔧  To list useful commands, type 'commands'.  \n\e[0m"
fi

# Source the .bashrc file to apply changes
source ~/.bashrc

# Execute any commands passed to the script
exec "$@"
