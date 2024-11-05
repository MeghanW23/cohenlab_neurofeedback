ssh -t -i "$DOCKER_SSH_PRIVATE_KEY_PATH" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "${CHID}@${E3_HOSTNAME}" \
    "export USER='$USER' && \
    export CHID='$CHID' && \
    export E3_PATH_TO_SETTINGS='$E3_PATH_TO_SETTINGS' && \
    bash '$E3_TESTING_LOCALIZER_COMPUTE_PATH'"
