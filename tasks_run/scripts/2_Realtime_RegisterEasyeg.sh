echo "Docker Private Key Path: $DOCKER_SSH_PRIVATE_KEY_PATH"
echo "CHID: $CHID"
echo "E3 Hostname: $E3_HOSTNAME"
echo "Username: $USER"
echo "E3 Settings.py Path: $E3_PATH_TO_SETTINGS"
echo "E3 Private Key Path: $E3_PRIVATE_KEY_PATH"
echo "ROI Mask Dir Path: $LOCAL_MASK_DIR_PATH"
echo "E3 Startup Registration Path: $E3_SETUP_REG_AND_COMPUTE_PATH"

echo "Starting SSH Now..."
ssh -t -i "$DOCKER_SSH_PRIVATE_KEY_PATH" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "${CHID}@${E3_HOSTNAME}" \
    "export USER='$USER' && \
    export CHID='$CHID' && \
    export E3_PATH_TO_SETTINGS='$E3_PATH_TO_SETTINGS' && \
    export E3_PRIVATE_KEY_PATH='$E3_PRIVATE_KEY_PATH' && \
    export LOCAL_MASK_DIR_PATH='$LOCAL_MASK_DIR_PATH' && \
    bash '$E3_SETUP_REG_AND_COMPUTE_PATH'"