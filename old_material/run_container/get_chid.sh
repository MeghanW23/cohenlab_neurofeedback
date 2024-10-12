#!/bin/bash

config_file="/workdir/run_container/users.txt"

echo "Checking for your username in the users file..."
if ! grep -q "$USERNAME" "$config_file"; then
  echo "Your username was not found in the shell users file."
  echo "To connect to e3 without a password, we will need to configure your ssh keys using your CHID."
  while true; do
    read -p "Please enter your CH ID: " chid
    if [[ "$chid" != ch* ]]; then
      echo "Please ensure your CH ID includes 'ch'."
    else
      echo "Ok, using CH ID: ${chid}."
      echo "${USERNAME}, ${chid}" >> "$config_file"
      echo "Your user information is added to ${config_file}:"
      grep "$USERNAME" "$config_file"
      break
    fi
  done
else
  echo "Your user information was found in the users file:"
  grep "$USERNAME" "$config_file"
  chid=$(grep "^$USERNAME," "$config_file" | awk -F', ' '{print $2}')

fi

echo "Adding your chid as an environment variable ..."
echo "export USER='${USERNAME}'" >> ~/.bashrc
echo "export CHID='${chid}'" >> ~/.bashrc # set user's chid as an environment env

source ~/.bashrc
