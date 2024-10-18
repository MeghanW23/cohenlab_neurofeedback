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
        docker run -it --rm \
          -e CHID="$CHID" \
          -e TZ="America/New_York" \
          -e DOCKER_SSH_PRIVATE_KEY_PATH="$DOCKER_SSH_PRIVATE_KEY_PATH" \
          -e E3_HOSTNAME="$E3_HOSTNAME" \
          -v "$LOCAL_PROJECT_DIRECTORY":"$DOCKER_PROJECT_DIRECTORY" \
          -v "$LOCAL_SAMBASHARE_DIR":"$DOCKER_SAMBASHARE_DIR" \
          --entrypoint "$DOCKER_PATH_TO_STARTUP_SCRIPT" \
          meghanwalsh/nfb_docker:latest \
          "$E3TRANSFER_SCRIPT"

      break

    elif [ "$choice" = "2" ]; then
      echo "Ok, Running the Clear Directory Script ..."

      docker run -it --rm \
        -e CHID="$CHID" \
        -e TZ="America/New_York" \
        -e DOCKER_SSH_PRIVATE_KEY_PATH="$DOCKER_SSH_PRIVATE_KEY_PATH" \
        -e E3_HOSTNAME="$E3_HOSTNAME" \
        -v "$LOCAL_PROJECT_DIRECTORY":"$DOCKER_PROJECT_DIRECTORY" \
        -v "$LOCAL_SAMBASHARE_DIR":"$DOCKER_SAMBASHARE_DIR" \
        --entrypoint "$DOCKER_PATH_TO_STARTUP_SCRIPT" \
        meghanwalsh/nfb_docker:latest \
        "$CLEARDIRS_SCRIPT"

      break
    elif [ "$choice" = "3" ]; then
      echo "Ok, ssh-ing into e3 ..."

      docker run -it --rm \
        -e CHID="$CHID" \
        -e TZ="America/New_York" \
        -e DOCKER_SSH_PRIVATE_KEY_PATH="$DOCKER_SSH_PRIVATE_KEY_PATH" \
        -e E3_HOSTNAME="$E3_HOSTNAME" \
        -v "$LOCAL_PROJECT_DIRECTORY":"$DOCKER_PROJECT_DIRECTORY" \
        -v "$LOCAL_SAMBASHARE_DIR":"$DOCKER_SAMBASHARE_DIR" \
        --entrypoint "$DOCKER_PATH_TO_STARTUP_SCRIPT" \
        meghanwalsh/nfb_docker:latest \
        "$SSH_COMMAND_SCRIPT"

      break
    else
      echo "Please choose '1', '2', or '3'"
    fi
  done
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
echo "(6) Register Mask with Fnirt on Local Machine"
echo "(7) Register Mask with Easyreg on E3"
echo "(8) Run Functional Localizer"
echo "(9) See Utility Tasks"

while true; do
  read -p "Please enter the number corresponding with the task you want to run: " choice
  if [ "$choice" = "1" ]; then
    # Setup X11 forwarding for graphical display in Docker
    echo "Setting xquartz permissions ..."
    xhost +

    docker run -it --rm \
      -e TZ="America/New_York" \
      -e DISPLAY=host.docker.internal:0 \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v "$LOCAL_PROJECT_DIRECTORY":"$DOCKER_PROJECT_DIRECTORY" \
      -v "$LOCAL_SAMBASHARE_DIR":"$DOCKER_SAMBASHARE_DIR" \
      --entrypoint "$DOCKER_PATH_TO_STARTUP_SCRIPT" \
      meghanwalsh/nfb_docker:latest \
      "$TEST_PYGAME_SCRIPT"

    break

  elif [ "$choice" = "2" ]; then
    echo "Running RIFG Task ..."

    echo "Setting xquartz permissions ..."
    xhost +

    docker run -it --rm \
      -e TZ="America/New_York" \
      -e DISPLAY=host.docker.internal:0 \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v "$LOCAL_PROJECT_DIRECTORY":"$DOCKER_PROJECT_DIRECTORY" \
      -v "$LOCAL_SAMBASHARE_DIR":"$DOCKER_SAMBASHARE_DIR" \
      --entrypoint "$DOCKER_PATH_TO_STARTUP_SCRIPT" \
      meghanwalsh/nfb_docker:latest \
      "$RIFG_TASK_SCRIPT"

    break

  elif [ "$choice" = "3" ]; then
    echo "Running MSIT Task ..."

    echo "Setting xquartz permissions ..."
    xhost +

    docker run -it --rm \
      -e TZ="America/New_York" \
      -e DISPLAY=host.docker.internal:0 \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v "$LOCAL_PROJECT_DIRECTORY":"$DOCKER_PROJECT_DIRECTORY" \
      -v "$LOCAL_SAMBASHARE_DIR":"$DOCKER_SAMBASHARE_DIR" \
      --entrypoint "$DOCKER_PATH_TO_STARTUP_SCRIPT" \
      meghanwalsh/nfb_docker:latest \
      "$MSIT_TASK_SCRIPT"

    break

  elif [ "$choice" = "4" ]; then
    echo "Running Rest Task ..."

    echo "Setting xquartz permissions ..."
    xhost +

    docker run -it --rm \
      -e TZ="America/New_York" \
      -e DISPLAY=host.docker.internal:0 \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v "$LOCAL_PROJECT_DIRECTORY":"$DOCKER_PROJECT_DIRECTORY" \
      -v "$LOCAL_SAMBASHARE_DIR":"$DOCKER_SAMBASHARE_DIR" \
      --entrypoint "$DOCKER_PATH_TO_STARTUP_SCRIPT" \
      meghanwalsh/nfb_docker:latest \
      "$REST_TASK_SCRIPT"

    break

  elif [ "$choice" = "5" ]; then
    echo "Running NFB Task ..."

    echo "Setting xquartz permissions ..."
    xhost +

    docker run -it --rm \
      -e TZ="America/New_York" \
      -e DISPLAY=host.docker.internal:0 \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v "$LOCAL_PROJECT_DIRECTORY":"$DOCKER_PROJECT_DIRECTORY" \
      -v "$LOCAL_SAMBASHARE_DIR":"$DOCKER_SAMBASHARE_DIR" \
      --entrypoint "$DOCKER_PATH_TO_STARTUP_SCRIPT" \
      meghanwalsh/nfb_docker:latest \
      "$NFB_TASK_SCRIPT"

    break

  elif [ "$choice" = "6" ]; then
    echo "Registering MNI Space Mask to Subject Space Via FNIRT/FNIRT"

    "$REGISTER_FNIRT_SCRIPT"

    break

  elif [ "$choice" = "7" ]; then
    echo "Registering MNI Space Mask to Subject Space Via Easyreg"

    docker run -it --rm \
      -e CHID="$CHID" \
      -e TZ="America/New_York" \
      -e DOCKER_SAMBASHARE_DIR="$DOCKER_SAMBASHARE_DIR" \
      -e E3_HOSTNAME="$E3_HOSTNAME" \
      -e E3_INPUT_FUNC_DATA_DIR="$E3_INPUT_FUNC_DATA_DIR" \
      -e PRIVATE_KEY_PATH="$DOCKER_SSH_PRIVATE_KEY_PATH" \
      -e E3_COMPUTE_PATH="$E3_COMPUTE_PATH" \
      -e TMP_OUTDIR_PATH="$DOCKER_TMP_OUTDIR_PATH" \
      -v "$LOCAL_PROJECT_DIRECTORY":"$DOCKER_PROJECT_DIRECTORY" \
      -v "$LOCAL_SAMBASHARE_DIR":"$DOCKER_SAMBASHARE_DIR" \
      --entrypoint "$DOCKER_PATH_TO_STARTUP_SCRIPT" \
      meghanwalsh/nfb_docker:latest \
      "$LOCAL_REGISTER_EASYREG_SCRIPT"

    break
  elif [ "$choice" = "8" ]; then
    echo "Ok, Running Functional Localizer ..."

    docker run -it --rm \
      -e TZ="America/New_York" \
      -e TMP_OUTDIR_PATH="$DOCKER_TMP_OUTDIR_PATH" \
      -v "$LOCAL_PROJECT_DIRECTORY":"$DOCKER_PROJECT_DIRECTORY" \
      -v "$LOCAL_SAMBASHARE_DIR":"$DOCKER_SAMBASHARE_DIR" \
      --entrypoint "$DOCKER_PATH_TO_STARTUP_SCRIPT" \
      meghanwalsh/nfb_docker:latest \
      "$LOCALIZER_FILE_PATH"

      break

  elif [ "$choice" = "9" ]; then
    run_utility_scripts
    break
  else
     echo "Please choose '1', '2', '3', '4','5', '6', '7', '8' or '9'"
  fi
done