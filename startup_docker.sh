#!/bin/bash

user_file="/workdir/users.txt"

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

echo "Setting up aliases ..."
./aliases_and_functions.sh
echo "Aliases Set."

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

echo "Exporting FSL Path Environment Variables ..."
# Append the necessary exports to .bashrc
echo "export FSLDIR=/usr/local/fsl" >> /root/.bashrc
echo "export PATH=\$FSLDIR/bin:\$PATH" >> /root/.bashrc
echo "export USER=$(whoami)" >> /root/.bashrc
echo ". \$FSLDIR/etc/fslconf/fsl.sh" >> /root/.bashrc

echo "Adding python virtual environment to ..."
echo "source /workdir/venv/bin/activate" >> ~/.bashrc

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
