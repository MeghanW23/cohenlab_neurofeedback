ssh -t -i "$DOCKER_SSH_PRIVATE_KEY_PATH" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "${CHID}@${E3_HOSTNAME}" \
    "export USER='$USER' && \
    export CHID='$CHID' && \
    export E3_PATH_TO_SETTINGS='$E3_PATH_TO_SETTINGS' && \
    export E3_PRIVATE_KEY_PATH='$E3_PRIVATE_KEY_PATH' && \
    export LOCAL_MASK_DIR_PATH='$LOCAL_MASK_DIR_PATH' && \
    bash '$E3_TESTING_LOCALIZER_COMPUTE_PATH'"