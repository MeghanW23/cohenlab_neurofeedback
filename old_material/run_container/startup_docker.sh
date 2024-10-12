#!/bin/bash

set -e

echo "This is the docker entrypoint script."
echo "NOTE: To setup SSH keys for the first time, you must be on the VPN"
source /workdir/run_container/get_chid.sh # Source the child script from the parent script (so it runs in the same shell)
config_file="/workdir/run_container/users.txt"
CHID=$(grep "^$USERNAME," "$config_file" | awk -F', ' '{print $2}')

echo "Checking for SSH keys ..."
if [ ! -f "/workdir/.ssh/docker_e3_key_$CHID" ]; then
  echo "No SSH Key Detected."
   /workdir/run_container/get_ssh_keys.sh
else
  echo "SSH keys found successfully."
  echo "Setting correct permissions for the e3 private key"
  chmod 600 /workdir/.ssh/docker_e3_key_"$CHID"
  echo "Permissions set."
fi

# create python virtual environment, if it doesnt already exist
echo "Checking for the existence of the Python virtual environment ..."
if [ ! -d "run_container/venv" ]; then
  while true; do
    read -p "Python virtual environment not found. Create the virtual env? (y/n) " create_choice
    if [ "$create_choice" = 'y' ]; then
      echo "Ok, creating virtual environment now ..."
      /workdir/run_container/make_venv.sh
      break
    else
      echo "Ok, I won't create the virtual environment. You can create it later by running the script: /workdir/run_container/make_venv.sh"
      break
    fi
  done
else
  echo "Found Python virtual environment successfully."
fi

echo "Setting aliases ..."
source /workdir/run_container/aliases.sh && echo "Aliases set."

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
