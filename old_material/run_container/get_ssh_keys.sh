#!/bin/bash

echo "Creating SSH Keys ..."

# Ensure CHID is set before running
config_file="/workdir/run_container/users.txt"
chid=$(grep "^$USERNAME," "$config_file" | awk -F', ' '{print $2}')
if [ -z "$chid" ]; then
  echo "chid environment variable is not set."
  exit 1
else
  # Create SSH Keys
  ssh-keygen -t rsa -f /workdir/.ssh/docker_e3_key_$chid -C "for e3 passwordless login via docker for '${chid}'"

  # Copy SSH Keys to E3
  ssh-copy-id -i /workdir/.ssh/docker_e3_key_$chid.pub $chid@e3-login.tch.harvard.edu

  # Create Config File
  touch /workdir/.ssh/config_$chid

  # Create known hosts so it doesnt think we are connecting to e3 for the first time with each new containter
  touch ~/.ssh/known_hosts_$chid

  # Create known hosts file so it doesn't think we are connecting to e3 for the first time with each new container
  touch /workdir/.ssh/known_hosts_$chid

  # Add to SSH config file
  cat <<EOL >> /workdir/.ssh/config_$chid
  Host e3_$chid
    HostName e3-login.tch.harvard.edu
    User $chid
    IdentityFile /workdir/.ssh/docker_e3_key_$chid
    ForwardAgent yes
    ForwardX11 yes
    ForwardX11Trusted yes
    UserKnownHostsFile=/workdir/.ssh/known_hosts_$chid
    StrictHostKeyChecking no

EOL

  chmod 600 /workdir/.ssh/docker_e3_key_$chid
  echo "SSH config for $chid created at /workdir/.ssh/config_$chid"



fi
