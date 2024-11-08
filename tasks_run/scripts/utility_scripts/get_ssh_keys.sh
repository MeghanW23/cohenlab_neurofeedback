#!/bin/bash

echo "Creating SSH Keys ..."

# Ensure CHID is set before running
if [ -z "$CHID" ]; then
  echo "CHID environment variable is not set."
  exit 1
fi

if [ -z "$SSH_DIRECTORY" ]; then 
  echo "Could not get necessary env var: SSH_DIRECTORY from docker run command."
  exit 1
fi 

if [ ! -d "$SSH_DIRECTORY" ]; then 
  echo "Could not find the SSH directory. Making it at: ${SSH_DIRECTORY}"
  mkdir "$SSH_DIRECTORY"
fi 

# Create SSH Keys
ssh-keygen -t rsa -f ${SSH_DIRECTORY}/docker_e3_key_$CHID -C "for e3 passwordless login via docker for '${CHID}'"
if [ $? -ne 0 ]; then
  echo "Error creating SSH keys."
  exit 1
fi

# Copy SSH Keys to E3
ssh-copy-id -i ${SSH_DIRECTORY}/docker_e3_key_$CHID.pub $CHID@e3-login.tch.harvard.edu
if [ $? -ne 0 ]; then
  echo "Error copying to E3."
  exit 1
fi

# Create Config File
touch ${SSH_DIRECTORY}/config_$CHID

# Create known hosts file so it doesn't think we are connecting to e3 for the first time with each new container
touch ${SSH_DIRECTORY}/known_hosts_$CHID

# Add to SSH config file
cat <<EOL >> $SSH_DIRECTORY/config_$CHID
Host e3_$CHID
    HostName e3-login.tch.harvard.edu
    User $CHID
    IdentityFile $SSH_DIRECTORY/docker_e3_key_$CHID
    ForwardAgent yes
    ForwardX11 yes
    ForwardX11Trusted yes
    UserKnownHostsFile=$SSH_DIRECTORY/known_hosts_$CHID
    StrictHostKeyChecking no
EOL

chmod 600 $SSH_DIRECTORY/docker_e3_key_$CHID

echo "SSH config for $CHID created at $SSH_DIRECTORY/config_$CHID"
