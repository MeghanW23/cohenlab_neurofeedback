#!/bin/bash

set -e

function run_utility_scripts {
  echo -e "\nUtility Tasks: "
  echo "(1) Transfer Files to/from E3"
  echo "(2) Run ClearDirs.py"
  echo ""


  while true; do
    read -p "Please enter the number corresponding with the utility task you want to run: " choice
    if [ "$choice" = "1" ]; then
      echo "Ok, Transferring Files to/from E3 ..."
      run_docker "$E3TRANSFER_SCRIPT"
      break
    elif [ "$choice" = "2" ]; then
      echo "Ok, Running the Clear Directory Script ..."
      run_docker "$CLEARDIR_SCRIPT"
      break
    else
      echo "Please choose '1' or '2'"
    fi
  done
}

function run_docker {
  local script_to_run=$1 # input script to run and assign it as the entrypoint script in the docker

  # Setup X11 forwarding for graphical display in docker
  echo "Setting xquartz permissions ..."
  xhost +

  docker run -it --rm \
    -e DISPLAY=host.docker.internal:0 \
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
}

echo -e "Getting env variables to use during docker container setup."
source config.env

echo "Choose Action: "
echo "(1) Run sample pygame script"
echo "(2) Do RIFG task"
echo "(3) Do MSIT Task"
echo "(4) Do Rest Task"
echo "(5) Do NFB Task"
echo "(6) Register Mask with Fnirt"
echo "(7) See Utility Tasks"

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
    echo "Registering MNI Space Mask to Subject Space Via FNIRT/FNIRT"
    "$REGISTER_FNIRT_SCRIPT"
    break
  elif [ "$choice" = "7" ]; then
    run_utility_scripts
    break
  else
     echo "Please choose '1', '2', '3', '4','5', '6', or '7'"
  fi
done