#!/bin/bash

# Store the current user for later
original_user=$(whoami)

# Switch to the target user and run a script
sudo -u samba_user 
/Users/samba_user/setpermissions.sh

# Switch back to the original user (optional, since the script 
# runs in the context of the shell)
# echo "Back to the original user: $original_user"

