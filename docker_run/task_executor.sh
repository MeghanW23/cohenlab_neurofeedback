#!/bin/bash

set -e

function run_utility_scripts {
  echo -e "\nUtility Tasks: "
  echo "(1) Transfer Files to/from E3"
  echo "(2) Run ClearDirs.py"
  echo "(3) Go to E3"


  while true; do
    read -p "Please enter the number corresponding with the utility task you want to run: " choice
    if [ "$choice" = "1" ]; then
      run_docker "$E3TRANSFER_SCRIPT"
      break
    elif [ "$choice" = "2" ]; then
      echo "Ok, Running the Clear Directory Script ..."
      run_docker "$CLEARDIR_SCRIPT"
      break
    elif [ "$choice" = "3" ]; then
      echo "Ok, ssh-ing into e3 ..."
      run_docker "$SSH_COMMAND_SCRIPT"
      break
    else
      echo "Please choose '1', '2', or '3'"
    fi
  done
}

function run_docker {
  local script_to_run=$1     # First argument is the script to run
  shift                      # Remove the first argument (script) so the rest are environment variables

  # Setup X11 forwarding for graphical display in Docker
  echo "Setting xquartz permissions ..."
  xhost +

  # Prepare the environment variables to pass to Docker
  env_vars=""
  while (( "$#" )); do       # Loop through the remaining arguments (environment variables)
    env_vars+="$1 "
    shift                    # Move to the next argument
  done

docker run -it --rm \
  -e DISPLAY=host.docker.internal:0 \
  -e DOCKER_CONFIG_FILE_PATH="$DOCKER_CONFIG_FILE_PATH" \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v "$LOCAL_DATA_AND_TASK_PATH":"$DOCKER_DATA_AND_TASK_PATH" \
  -v "$LOCAL_RUN_DOCKER_DIR_PATH":"$DOCKER_RUN_DOCKER_DIR_PATH" \
  -v "$LOCAL_SSH_KEY_PATH":"$DOCKER_SSH_KEY_PATH" \
  -v "$LOCAL_SAMBASHARE_DIR":"$DOCKER_SAMBASHARE_DIR" \
  -v "$LOCAL_SSH_DIR":"$DOCKER_SSH_DIR" \
  --entrypoint "$DOCKER_SETUP_CONTAINER_FILE_PATH" \
  meghanwalsh/nfb_docker:latest \
  "$script_to_run"


  echo "Docker container has exited."
}


echo -e "Getting env variables to use during docker container setup."
local_dir=$(dirname "$(realpath "$0")")
source "$local_dir"/config.env

echo "Choose Action: "
echo "(1) Run sample pygame script"
echo "(2) Do RIFG task"
echo "(3) Do MSIT Task"
echo "(4) Do Rest Task"
echo "(5) Do NFB Task"
echo "(6) Register Mask with Fnirt"
echo "(7) Register Mask with Easyreg"
echo "(8) See Utility Tasks"

while true; do
  read -p "Please enter the number corresponding with the task you want to run: " choice
  if [ "$choice" = "1" ]; then
    echo "Running Test Pygame script ... "
    run_docker "$TEST_PYGAME_SCRIPT"
    break

  elif [ "$choice" = "2" ]; then
    echo "Running RIFG Task ..."
    run_docker "$RIFG_TASK_SCRIPT"
    break

  elif [ "$choice" = "3" ]; then
    echo "Running MSIT Task ..."
    run_docker "$MSIT_TASK_SCRIPT"
    break

  elif [ "$choice" = "4" ]; then
    echo "Running Rest Task ..."
    run_docker "$REST_TASK_SCRIPT"
    break

  elif [ "$choice" = "5" ]; then
    echo "Running NFB Task ..."
    run_docker "$NFB_TASK_SCRIPT"
    break

  elif [ "$choice" = "6" ]; then
    # Fnirt is run locally
    echo "Registering MNI Space Mask to Subject Space Via FNIRT/FNIRT"
    "$REGISTER_FNIRT_SCRIPT"
    break

  elif [ "$choice" = "7" ]; then
    echo "Registering MNI Space Mask to Subject Space Via Easyreg"
      # Setup X11 forwarding for graphical display in Docker
      echo "Setting xquartz permissions ..."
      xhost +

    docker run -it --rm \
      -e DISPLAY=host.docker.internal:0 \
      -e DOCKER_CONFIG_FILE_PATH="$DOCKER_CONFIG_FILE_PATH" \
      -e DOCKER_SAMBASHARE_DIR="$DOCKER_SAMBASHARE_DIR" \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v "$LOCAL_DATA_AND_TASK_PATH":"$DOCKER_DATA_AND_TASK_PATH" \
      -v "$LOCAL_RUN_DOCKER_DIR_PATH":"$DOCKER_RUN_DOCKER_DIR_PATH" \
      -v "$LOCAL_SSH_KEY_PATH":"$DOCKER_SSH_KEY_PATH" \
      -v "$LOCAL_SAMBASHARE_DIR":"$DOCKER_SAMBASHARE_DIR" \
      -v "$LOCAL_SSH_DIR":"$DOCKER_SSH_DIR" \
      --entrypoint "$DOCKER_SETUP_CONTAINER_FILE_PATH" \
      meghanwalsh/nfb_docker:latest \
      "$LOCAL_REGISTER_EASYREG_SCRIPT"
    break

  elif [ "$choice" = "8" ]; then
    run_utility_scripts
    break
  else
     echo "Please choose '1', '2', '3', '4','5', '6', or '7'"
  fi
done