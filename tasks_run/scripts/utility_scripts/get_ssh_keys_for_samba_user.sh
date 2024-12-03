#!/bin/bash

echo "Creating SSH Keys for passwordless ssh from local user to samba_user..."

# Ensure CHID is set before running
if [ -z "$CHID" ]; then
  echo "CHID environment variable is not set."
  exit 1
fi

# Ensure USER is set correctly before running
if [ -z "$USER" ]; then
  echo "USER environment variable is not set."
  echo "Using \$(whoami) command..."
  export USER="$(whoami)"
  exit 1
fi

if [ "$USER" = "samba_user" ]; then
    echo "You are on your samba_user acount."
    echo "Please switch to the account you would like to ssh into the samba_user account from."
    exit 1
fi 

# Make sure SSH Directory is setup
if [ -z "$SSH_DIRECTORY" ]; then 
  echo "Could not get necessary env var: SSH_DIRECTORY."
  exit 1
fi 

if [ ! -d "$SSH_DIRECTORY" ]; then 
  echo "Could not find the SSH directory. Making it at: ${SSH_DIRECTORY}"
  mkdir "$SSH_DIRECTORY"
fi 

# Create SSH Keys
ssh-keygen -t rsa -f ${SSH_DIRECTORY}/local_for_samba_user_$CHID -C "for passwordless login to samba_user account for '${CHID}'"
if [ $? -ne 0 ]; then
  echo "Error creating SSH keys."
  exit 1
fi

# Copy SSH Keys to samba_user
ssh-copy-id -i ${SSH_DIRECTORY}/local_for_samba_user_$CHID.pub samba_user@localhost
if [ $? -ne 0 ]; then
  echo "Error copying."
  exit 1
fi

# Create Config File if it doesnt exist
touch ${SSH_DIRECTORY}/config_$CHID

# Create known hosts file if it doesnt exist
touch ${SSH_DIRECTORY}/known_hosts_$CHID

# Add to SSH config file
cat <<EOL >> $SSH_DIRECTORY/config_$CHID
Host samba_user_$CHID
    HostName localhost
    User $USER
    IdentityFile $SSH_DIRECTORY/local_for_samba_user_$CHID
    ForwardAgent yes
    ForwardX11 yes
    ForwardX11Trusted yes
    UserKnownHostsFile=$SSH_DIRECTORY/known_hosts_$CHID
    StrictHostKeyChecking no
EOL

chmod 600 $SSH_DIRECTORY/local_for_samba_user_$CHID

echo "SSH config for $CHID at $SSH_DIRECTORY/config_$CHID"

echo "To run, type: "
echo "ssh -i ${SSH_DIRECTORY}/local_for_samba_user_$CHID samba_user@localhost"
