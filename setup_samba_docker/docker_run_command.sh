#!/bin/bash 

settings_script_path="$(dirname $(dirname "$(realpath "$0")"))/tasks_run/scripts/settings.py"
export LOCAL_SAMBASHARE_DIR_PATH="$(python3 ${settings_script_path} LOCAL_SAMBASHARE_DIR_PATH -s)"
export SMB_CONF_FILE_PATH="$(python3 ${settings_script_path} SMB_CONF_FILE_PATH -s)"

docker run -d --rm \
    --name samba \
    -e USER_UID=$(id -u $(whoami)) \
    -e USER_GID=$(id -g $(whoami)) \
    -e USER_NAME=smbuser \
    -p 139:139 \
    -p 445:445 \
    -v ${LOCAL_SAMBASHARE_DIR_PATH}:/sambashare \
    -v ${SMB_CONF_FILE_PATH}:/etc/samba/smb.conf \
    meghanwalsh/nfb_samba_share:latest bash -c "systemctl start smbd && systemctl enable smbd && tail -f /dev/null"