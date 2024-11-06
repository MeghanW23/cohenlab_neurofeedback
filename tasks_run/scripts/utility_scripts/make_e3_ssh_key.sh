#!/bin/bash

if [ -z ${E3_PATH_TO_SETTINGS} ]; then
    echo "Could not find env var E3_PATH_TO_SETTINGS"
    exit 1 
fi

echo "Using SSH Private Key at: ${DOCKER_SSH_PRIVATE_KEY_PATH}"
chmod 600 "$DOCKER_SSH_PRIVATE_KEY_PATH"

echo ""
echo "--------------------------------------------------------------------------------------------------"
echo "Run Script: /lab-share/Neuro-Cohen-e2/Public/projects/ADHD_NFB/ssh/make_ssh_key.sh when in e3 term"
echo "--------------------------------------------------------------------------------------------------"
echo ""

ssh -i "$DOCKER_SSH_PRIVATE_KEY_PATH" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "${CHID}@${E3_HOSTNAME}" \