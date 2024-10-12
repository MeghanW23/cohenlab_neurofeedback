#!/bin/bash

set -e
echo "Setting xquartz permissions ..."
xhost +

echo "Getting env variables to use during docker container setup ..."
local_dir_path=$(dirname "$(realpath "$0")")
source "${local_dir_path}/config.env"

# Run the Docker container
echo "Running the docker container now ..."

echo "Choose Action: "
echo "(1) Run sample pygame script"
echo "(2) Do RIFG task"
echo "(3) Transfer files to E3"
options=(1 2 3)
script_to_run=""
while true; do
  read -p "Please enter the number corresponding with the task you want to run (1/2/3) : " choice
  if echo "${options[@]}" | grep -qw "$choice"; then
    if [ $choice = "1" ]; then
      echo "Running Test Pygame script ... "
      script_to_run="$TEST_PYGAME_SCRIPT"
    elif [ "$choice" = "2" ]; then
      echo "Running RIFG Task ..."
      script_to_run="$RIFG_SCRIPT"
    elif [ "$choice" = "3" ]; then
      echo "Running E3 transfer script ..."
      script_to_run="$E3TRANSFER_SCRIPT"
    fi
    break
  else
    echo "Please choose either '1' or '2' or '3'"
  fi
done


docker run -it --rm \
  -e DISPLAY="$DISPLAY" \
  -e DOCKER_CONFIG_FILE_PATH="$DOCKER_CONFIG_FILE_PATH" \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v "$LOCAL_DATA_AND_TASK_PATH":"$DOCKER_DATA_AND_TASK_PATH" \
  -v "$LOCAL_RUN_DOCKER_DIR_PATH":"$DOCKER_RUN_DOCKER_DIR_PATH" \
  -v "$LOCAL_SSH_KEY_PATH":"$DOCKER_SSH_KEY_PATH" \
  --entrypoint "$DOCKER_SETUP_CONTAINER_FILE_PATH" \
  meghanwalsh/nfb_docker:latest \
  "$script_to_run" \

echo "Docker container has exited."


