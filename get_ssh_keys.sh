#!/bin/bash

echo "Creating SSH Keys ..."

# Ensure CHID is set before running
if [ -z "$CHID" ]; then
  echo "CHID environment variable is not set."
  exit 1
fi

# Create SSH Keys
ssh-keygen -t rsa -f /workdir/.ssh/docker_e3_key_$CHID -C "for e3 passwordless login via docker for '${CHID}'"

# Copy SSH Keys to E3
ssh-copy-id -i /workdir/.ssh/docker_e3_key_$CHID.pub $CHID@e3-login.tch.harvard.edu

# Create Config File
touch /workdir/.ssh/config_$CHID

# Add to config file
cat <<EOL >> /workdir/.ssh/config_$CHID
Host e3_$CHID
    HostName e3-login.tch.harvard.edu
    User $CHID
    IdentityFile /workdir/.ssh/docker_e3_key_$CHID
    ForwardAgent yes
    ForwardX11 yes
    ForwardX11Trusted yes
EOL

echo "SSH config for $CHID created at /workdir/.ssh/config_$CHID"
