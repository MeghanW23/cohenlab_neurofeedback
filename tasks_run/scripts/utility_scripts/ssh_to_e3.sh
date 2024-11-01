#!/bin/bash
echo "Using SSH Private Key at: ${DOCKER_SSH_PRIVATE_KEY_PATH}"

chmod 600 "$DOCKER_SSH_PRIVATE_KEY_PATH"
ssh -i "$DOCKER_SSH_PRIVATE_KEY_PATH" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "${CHID}@${E3_HOSTNAME}"
