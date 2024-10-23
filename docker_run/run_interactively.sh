  docker run -it --rm \
    -e DISPLAY=host.docker.internal:0 \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v "$LOCAL_PROJECT_DIRECTORY":"$DOCKER_PROJECT_DIRECTORY" \
    -v "$LOCAL_SAMBASHARE_DIR":"$DOCKER_SAMBASHARE_DIR" \
    --entrypoint "$DOCKER_SETUP_CONTAINER_FILE_PATH" \
    meghanwalsh/nfb_docker:latest \
    /bin/bash