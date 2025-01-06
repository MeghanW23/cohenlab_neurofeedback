#!/bin/bash 

# Current ran via ../docker_run/boot_samba_container.sh
LOCAL_SAMBASHARE_DIR_PATH="/Users/samba_user/sambashare"

docker run -d \
    --name samba \
    -e USER_UID=$(id -u $(whoami)) \
    -e USER_GID=$(id -g $(whoami)) \
    -e USER_NAME=smbuser \
    -p 139:139 \
    -p 445:445 \
    -v ${LOCAL_SAMBASHARE_DIR_PATH}:/sambashare \
    meghanwalsh/nfb_samba_share:latest bash -c "systemctl start smbd && tail -f /dev/null"