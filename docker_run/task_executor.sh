#!/bin/bash


function run_utility_scripts {
  CHID="$1"

  echo -e "\nUtility Tasks: "
  echo "(1) Transfer Files to/from E3"
  echo "(2) Run ClearDirs.py"
  echo "(3) Go to E3"
  echo "(4) Compare E3 settings file to local"
  echo " " 


  while true; do
    read -p "Please enter the number corresponding with the utility task you want to run: " choice
    if [ "$choice" = "1" ]; then
        docker run -it --rm \
          -e CHID="$CHID" \
          -e TZ="$(python "$settings_script_path" TZ -s)" \
          -e DOCKER_SSH_PRIVATE_KEY_PATH="$(python "$settings_script_path" docker LOCAL_PATH_TO_PRIVATE_KEY -s)" \
          -e E3_HOSTNAME="$(python "$settings_script_path" E3_HOSTNAME -s)" \
          -e TRANSFER_FILES_SCRIPT="$(python "$settings_script_path" docker TRANSFER_FILES_SCRIPT -s)" \
          -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
          -v "$(python "$settings_script_path" LOCAL_SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
          --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
          meghanwalsh/nfb_docker:latest \
          "$(python "$settings_script_path" docker TRANSFER_FILES_SCRIPT -s)"

      break

    elif [ "$choice" = "2" ]; then
      echo "Ok, Running the Clear Directory Script ..."

      docker run -it --rm \
        -e CHID="$CHID" \
        -e TZ="$(python "$settings_script_path" TZ -s)" \
        -e PRIVATE_KEY_PATH="$(python "$settings_script_path" docker LOCAL_PATH_TO_PRIVATE_KEY -s)" \
        -e E3_HOSTNAME="$(python "$settings_script_path" E3_HOSTNAME -s)" \
        -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
        -v "$(python "$settings_script_path" LOCAL_SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
        --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
        meghanwalsh/nfb_docker:latest \
        "$(python "$settings_script_path" docker CLEAR_DIRS_SCRIPT -s)"

      break
    elif [ "$choice" = "3" ]; then
      echo "Ok, ssh-ing into e3 ..."

      docker run -it --rm \
        -e CHID="$CHID" \
        -e TZ="$(python "$settings_script_path" TZ -s)" \
        -e DOCKER_SSH_PRIVATE_KEY_PATH="$(python "$settings_script_path" docker LOCAL_PATH_TO_PRIVATE_KEY -s)" \
        -e E3_HOSTNAME="$(python "$settings_script_path" E3_HOSTNAME -s)" \
        -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
        -v "$(python "$settings_script_path" LOCAL_SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
        --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
        meghanwalsh/nfb_docker:latest \
        "$(python "$settings_script_path" docker SSH_COMMAND_SCRIPT -s)" \

      break

    elif [ "$choice" = "4" ]; then
      echo "Ok, comparing settings files..." 
    
      docker run -it --rm \
        -e CHID="$CHID" \
        -e TZ="$(python "$settings_script_path" TZ -s)" \
        -e DOCKER_SSH_PRIVATE_KEY_PATH="$(python "$settings_script_path" docker LOCAL_PATH_TO_PRIVATE_KEY -s)" \
        -e E3_HOSTNAME="$(python "$settings_script_path" E3_HOSTNAME -s)" \
        -e E3_SETTINGS="$(python "$settings_script_path" docker E3_PATH_TO_SETTINGS -s)" \
        -e LOCAL_SETTINGS="$(python3 "$settings_script_path" docker SETTINGS_PATH -s)" \
        -e PRIVATE_KEY="$(python3 "$settings_script_path" docker LOCAL_PATH_TO_PRIVATE_KEY -s)" \
        -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
        -v "$(python "$settings_script_path" LOCAL_SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
        --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
        meghanwalsh/nfb_docker:latest \
        "$(python "$settings_script_path" docker COMPARE_SETTINGS_SCRIPT -s)" \
      
      break
      
    else
      echo "Please choose '1', '2', or '3'"
    fi
  done
}

# get settings path and user file path 
settings_script_path="$(dirname $(dirname "$(realpath "$0")"))/tasks_run/scripts/settings.py"
script_dir=$(dirname "$settings_script_path")
user_file=$(python "$settings_script_path" USERS_FILE -s)

# get chid and users from userfile path
user_info=$(grep $(whoami) "$user_file")
if [ -z "$user_info" ]; then
    echo "I could not find your chid and user name in the users file (${user_file})"
    echo "Please enter your information in that file like this:"
    echo ""
    echo "$(whoami),<your_child>"
    echo ""
    echo "then you can re-run this script"
    exit 1
fi

IFS=',' read -r USER CHID <<< "$user_info"
export "USER=$USER"
export "CHID=$CHID"

echo " "
echo "Your Registered Information: "
echo "Name: $USER"
echo "Childrens ID: $CHID"
echo " "
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
echo " "
while true; do
  read -p "Please enter the number corresponding with the task you want to run: " choice
  if [ "$choice" = "1" ]; then
    # Setup X11 forwarding for graphical display in Docker
    echo "Setting xquartz permissions ..."
    xhost +

    docker run -it --rm \
      -e TZ="$(python "$settings_script_path" TZ -s)" \
      -e DISPLAY=host.docker.internal:0 \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
      -v "$(python "$settings_script_path" LOCAL_SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
      --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
      meghanwalsh/nfb_docker:latest \
      "$(python "$settings_script_path" docker TEST_PYGAME_SCRIPT -s)"

    break

  elif [ "$choice" = "2" ]; then
    echo "Running RIFG Task ..."

    echo "Setting xquartz permissions ..."
    xhost +

    docker run -it --rm \
      -e TZ="$(python "$settings_script_path" TZ -s)" \
      -e DISPLAY=host.docker.internal:0 \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
      -v "$(python "$settings_script_path" LOCAL_SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
      --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
      meghanwalsh/nfb_docker:latest \
      "$(python "$settings_script_path" docker RIFG_TASK_SCRIPT -s)"

    break

  elif [ "$choice" = "3" ]; then
    echo "Running MSIT Task ..."

    echo "Setting xquartz permissions ..."
    xhost +

    docker run -it --rm \
      -e TZ="$(python "$settings_script_path" TZ -s)" \
      -e DISPLAY=host.docker.internal:0 \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
      -v "$(python "$settings_script_path" LOCAL_SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
      --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
      meghanwalsh/nfb_docker:latest \
      "$(python "$settings_script_path" docker MSIT_TASK_SCRIPT -s)"

    break

  elif [ "$choice" = "4" ]; then
    echo "Running Rest Task ..."

    echo "Setting xquartz permissions ..."
    xhost +

    docker run -it --rm \
      -e TZ="$(python "$settings_script_path" TZ -s)" \
      -e DISPLAY=host.docker.internal:0 \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
      -v "$(python "$settings_script_path" LOCAL_SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
      --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
      meghanwalsh/nfb_docker:latest \
      "$(python "$settings_script_path" docker REST_TASK_SCRIPT -s)"

    break

  elif [ "$choice" = "5" ]; then
    echo "Running NFB Task ..."

    echo "Setting xquartz permissions ..."
    xhost +

    docker run -it --rm \
      -e TZ="$(python "$settings_script_path" TZ -s)" \
      -e DISPLAY=host.docker.internal:0 \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
      -v "$(python "$settings_script_path" LOCAL_SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
      --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
      meghanwalsh/nfb_docker:latest \
      "$(python "$settings_script_path" docker NFB_TASK_SCRIPT -s)"

    break

  elif [ "$choice" = "6" ]; then
    echo "Registering MNI Space Mask to Subject Space Via FNIRT/FNIRT"

    echo "Setting up environment variables needed ..."
    export LOCAL_SAMBASHARE_DIR="$(python "$settings_script_path" LOCAL_SAMBASHARE_DIR_PATH -s)"
    export TMP_OUTDIR_PATH="$(python "$settings_script_path" TMP_OUTDIR_PATH -s)"
    export MNI_BRAIN_PATH="$(python "$settings_script_path" MNI_BRAIN_PATH -s)"
    export MNI_ACC_MASK_PATH="$(python "$settings_script_path" MNI_ACC_MASK_PATH -s)"
    export MNI_MOTOR_MASK_PATH="$(python "$settings_script_path" MNI_MOTOR_MASK_PATH -s)"
    export MNI_RIFG_MASK_PATH="$(python "$settings_script_path" MNI_RIFG_MASK_PATH -s)"
    
    echo "Calling script ..."
    "$(python "$settings_script_path" REGISTER_FNIRT_SCRIPT -s)"

    break

  elif [ "$choice" = "7" ]; then
    echo "Registering MNI Space Mask to Subject Space Via Easyreg"

    docker run -it --rm \
      -e CHID="$CHID" \
      -e USER="$USER" \
      -e TZ="$(python "$settings_script_path" TZ -s)" \
      -e DOCKER_SAMBASHARE_DIR="$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
      -e E3_HOSTNAME="$(python "$settings_script_path" E3_HOSTNAME -s)" \
      -e E3_INPUT_FUNC_DATA_DIR="$(python "$settings_script_path" E3_PATH_TO_INPUT_FUNC_DATA -s)" \
      -e PRIVATE_KEY_PATH="$(python "$settings_script_path" docker LOCAL_PATH_TO_PRIVATE_KEY -s)" \
      -e E3_COMPUTE_PATH="$(python "$settings_script_path" E3_COMPUTE_PATH -s)" \
      -e TMP_OUTDIR_PATH="$(python "$settings_script_path" docker TMP_OUTDIR_PATH -s)" \
      -e E3_PATH_TO_OUTPUT_MASK="$(python "$settings_script_path" E3_PATH_TO_OUTPUT_MASK -s)" \
      -e ROI_MASK_DIR_PATH="$(python "$settings_script_path" docker ROI_MASK_DIR_PATH -s)" \
      -e ROI_MASK_DIR_PATH="$(python "$settings_script_path" ROI_MASK_DIR_PATH -s)" \
      -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
      -v "$(python "$settings_script_path" LOCAL_SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
      --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
      meghanwalsh/nfb_docker:latest \
      "$(python "$settings_script_path" docker REGISTER_EASYREG_SCRIPT -s)"

    break
  elif [ "$choice" = "8" ]; then
    echo "Ok, Running Functional Localizer ..."
    python "$(python "$settings_script_path" LOCALIZER_SCRIPT -s)"
    break

  elif [ "$choice" = "9" ]; then
    run_utility_scripts "$CHID"
    break
  else
     echo "Please choose '1', '2', '3', '4','5', '6', '7', '8' or '9'"
  fi
done