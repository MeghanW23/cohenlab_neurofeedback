#!/bin/bash

local_dir=$(dirname "$(realpath "$0")")
source "$local_dir"/config.env

echo "Using SSH Private Key at: ${DOCKER_SSH_PRIVATE_KEY_PATH}"
chmod 600 "$DOCKER_SSH_PRIVATE_KEY_PATH"
ssh -i "${DOCKER_SSH_PRIVATE_KEY_PATH}" "${CHID}@${E3_HOSTNAME}"
