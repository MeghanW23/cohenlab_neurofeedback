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
echo "(3) Do MSIT Task"
echo "(4) Do Rest Task"
echo "(5) Do NFB Task"

options=(1 2 3 4 5)
script_to_run=""
while true; do
  read -p "Please enter the number corresponding with the task you want to run (1/2/3/4/5) : " choice
  if echo "${options[@]}" | grep -qw "$choice"; then
    if [ $choice = "1" ]; then
      echo "Running Test Pygame script ... "
      script_to_run="$TEST_PYGAME_SCRIPT"

    elif [ "$choice" = "2" ]; then
      echo "Running RIFG Task ..."
      script_to_run="$RIFG_TASK_SCRIPT"

    elif [ "$choice" = "3" ]; then
      echo "Running MSIT Task ..."
      script_to_run="$MSIT_TASK_SCRIPT"

    elif [ "$choice" = "4" ]; then
      echo "Running Rest Task ..."
      script_to_run="$REST_TASK_SCRIPT"

    elif [ "$choice" = "5" ]; then
      echo "Running NFB Task ..."
      script_to_run="$NFB_TASK_SCRIPT"
    fi
    break
  else
    echo "Please choose '1', '2', '3', '4', or '5'"
  fi
done


docker run -it --rm \
  -e DISPLAY="$DISPLAY" \
  -e DOCKER_CONFIG_FILE_PATH="$DOCKER_CONFIG_FILE_PATH" \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v "$LOCAL_DATA_AND_TASK_PATH":"$DOCKER_DATA_AND_TASK_PATH" \
  -v "$LOCAL_RUN_DOCKER_DIR_PATH":"$DOCKER_RUN_DOCKER_DIR_PATH" \
  -v "$LOCAL_SSH_KEY_PATH":"$DOCKER_SSH_KEY_PATH" \
  -v "$LOCAL_SAMBASHARE_DIR":"$DOCKER_SAMBASHARE_DIR" \
  --entrypoint "$DOCKER_SETUP_CONTAINER_FILE_PATH" \
  meghanwalsh/nfb_docker:latest \
  "$script_to_run" \

echo "Docker container has exited."


