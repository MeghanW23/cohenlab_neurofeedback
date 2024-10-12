#!/bin/bash

set -e
echo "Setting xquartz permissions ..."
xhost +

echo "Getting env variables to use during docker container setup ..."
local_dir_path=$(dirname "$(realpath "$0")")
source "${local_dir_path}/config.env"

# Run the Docker container
echo "Running the docker container now ..."

echo "Scripts to run: "
echo "(1) Test Pygame"
echo "(2) RIFG Task"

script_to_run=""
while true; do
  options=(1 2)
  read -p "Please enter the number corresponding with the task you want to run (1/2) : " choice
  if echo "${options[@]}" | grep -qw "$choice"; then
    echo "Ok, running that script ... "
    if [ $choice = "1" ]; then
      echo "Running Test Pygame script ... "
      script_to_run="$TEST_PYGAME_SCRIPT"
    elif [ "$choice" = "2" ]; then
      echo "Running RIFG Task ..."
      script_to_run="$RIFG"
    fi
    # other stuff
    break
  else
    echo "Please choose either '1' or '2'"
  fi
done


docker run -it --rm \
  -e DISPLAY="$DISPLAY" \
  -e DOCKER_CONFIG_FILE_PATH="$DOCKER_CONFIG_FILE_PATH" \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v "$LOCAL_DATA_AND_TASK_PATH":"$DOCKER_DATA_AND_TASK_PATH" \
  -v "$LOCAL_RUN_DOCKER_DIR_PATH":"$DOCKER_RUN_DOCKER_DIR_PATH" \
  --entrypoint "$DOCKER_SETUP_CONTAINER_FILE_PATH" \
  meghanwalsh/nfb_docker:latest \
  "$script_to_run" \

echo "Docker container has exited."


