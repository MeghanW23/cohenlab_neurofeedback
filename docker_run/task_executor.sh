#!/bin/bash

function check_wifi_network {
  wifi_network=$(networksetup -getairportnetwork en0 | sed 's/^Current Wi-Fi Network: //' | tr -d '[:space:]')
  if [ "$wifi_network" != "TCH" ]; then 
    echo "Your Wifi Network is: ${wifi_network}. The reccommended wifi network is: TCH"
    read -p "Press Enter to Continue anyways. Type 'x' and then Enter to exit. " diff_wifi_continue
    diff_wifi_continue=$(echo "$diff_wifi_continue" | tr -d 's') # remove 's' presses from the scanner 
    if [ "$diff_wifi_continue" = "x" ]; then
      echo "Ok, exiting now ..."
      exit 0
    else
      echo "Ok, continuing ..."
    fi
  fi 
}
function check_access {
  settings_script_path="$1"

  project_directory=$(python "$settings_script_path" PROJECT_DIRECTORY -s)
  if [ -r "$project_directory" ] && [ -w "$project_directory" ] && [ -x "$project_directory" ]; then
    echo "You have full access (read, write, execute) to the project directory."
  else
    echo "You do not have full access (read, write, execute) to the project directory: ${project_directory}."
    read -p "Most, if not all scripts in this project need full access. Press Enter to Continue anyways. Type 'x' and then Enter to exit. " no_access_continue
    no_access_continue=$(echo "$no_access_continue" | tr -d 's')
    if [ "$no_access_continue" = "x" ]; then 
      echo "Ok, exiting..."
      exit 0
    else
     echo "Ok, continuing anyways..."
    fi
  fi

}
function registered_info {
  user_file="$1"

  # get chid and users from userfile path
  user_info=$(grep $(whoami) "$user_file")
  if [ -z "$user_info" ]; then
    echo ""
    echo "I could not find your Children's ID and Local Username in the users file (${user_file})."
    echo "Your Local Username and Children's ID are used in scripts involving accessing e3."
    read -p "Type 'y' to register your information now. Type any other key to continue without registering. " register_info
    register_info=$(echo "$register_info" | tr -d 's')
    if [ "$register_info" = "y" ]; then
      USER=$(whoami)
      export "USER=$USER"
      CHID=""
      while true; do
        read -p "Please enter your Children's ID (starting with 'ch'): " CHID
        CHID=$(echo "$CHID" | tr -d 's')
        read -p "Accept CHID: '${CHID}'? (enter 'y' to accept): " accept_CHID
        accept_CHID=$(echo "$accept_CHID" | tr -d 's')
        
        if [ "$accept_CHID" == "y" ]; then
          echo "Ok, using CHID: ${CHID}"
          export CHID="$CHID"
          break
        else
          echo "Try again."
        fi
      done

      line_to_add="${USER},${CHID}"
      echo "Adding your user information: "
      echo "${line_to_add}"
      echo "to the users file at: ${user_file}"
      echo "$line_to_add" >> "$user_file"
    fi
  else
    IFS=',' read -r USER CHID <<< "$user_info"
    export "USER=$USER"
    export "CHID=$CHID"
  fi
}
function check_for_priv_key {
  settings_script_path="$1"

  key_path=$(python "$settings_script_path" LOCAL_PATH_TO_PRIVATE_KEY -s)
  if [ ! -f "$key_path" ]; then
    echo " "
    echo "Path to your E3 private key: ${key_path} could not be found."
    echo "If you would like to make ssh-ing from the docker containers to e3 passwordless, please run select 'See Utility Tasks' and then 'Make SSH Keys from Passwordless SSH (from Local to E3)'"
    read -p "Press Enter to Continue. "
  else
    echo "Local E3 Private Key Path: ${key_path}"
  fi
}
function check_permissions_setter {
  settings_script_path="$1"

  echo "Checking if the permissions-setting script is running..."

  # Get Paths and Process ID 
  permissions_script=$(python "$settings_script_path" PERMISSIONS_SETTING_SCRIPT -s)
  if [ ! -f "$permissions_script" ]; then 
    echo "Permissions-setting script: ${permissions_script} does not exist."
    exit 1
  fi 

  run_permissions_script=$(python "$settings_script_path" RUN_PERMISSIONS_SETTING_SCRIPT -s)
  if [ ! -f "$run_permissions_script" ]; then 
    echo "Script to Run Permissions Setting Script: ${run_permissions_script} does not exist"
    exit 1
  fi 
  
  process_id_textfile=$(python "$settings_script_path" PROCESS_ID_TEXTFILE -s)
  if [ ! -f "$process_id_textfile" ]; then 
    echo "Process ID Storing Textfile: ${process_id_textfile} does not exist"
    exit 1
  else
    PID="$(cat $process_id_textfile)"
    if [ -z "$PID" ]; then 
      echo "Process ID associated with permissions-setting script was not found. I will assume the permissions-setting script is not running."
      while true; do
        read -p "Start running the permission-setting script? (y/n)" run_perm_setter
        if [ "$run_perm_setter" = "y" ]; then 
          echo "Ok, starting up the permission-setting script now ..."
          break
        elif [ "$run_perm_setter" = "n" ]; then
          echo "Ok, continuing without permission setting..."
          break
        else
          echo "Please enter either 'y' or 'n'"
        fi 
      done
    else
      if sudo kill -0 $PID 2>/dev/null; then
        echo "Permissions-setting script is already running. Continuing..." 
      else
        echo "Permission-settings script is not running."
        while true; do
          read -p "Start running the permission-setting script? (y/n): " run_perm_setter
          if [ "$run_perm_setter" = "y" ]; then 
            echo "Ok, starting up the permission-setting script now ..."
            "$run_permissions_script"
            echo "Continuing task executor now ..."

            break
          elif [ "$run_perm_setter" = "n" ]; then
            echo "Ok, continuing without permission setting..."
            sleep 0.2 # to allow experimenter to read above words before continuing 
            break
          else
            echo "Please enter either 'y' or 'n'. Try again. "
          fi 
        done
      fi
    fi
  fi 
}
function run_utility_scripts {
  CHID="$1"
  settings_script_path="$2"

  echo -e "\nUtility Tasks: "
  echo "(1) Transfer Files to/from E3"
  echo "(2) Run ClearDirs.py"
  echo "(3) Go to E3"
  echo "(4) Compare E3 settings file to local"
  echo "(5) Make a virtual environment via conda to run scripts locally"
  echo "(6) Make SSH Keys for Passwordless SSH from Local to E3"
  echo "(7) Run Old Localizer"
  echo " " 

  while true; do
    read -p "Please enter the number corresponding with the utility task you want to run: " choice
    choice=$(echo "$choice" | tr -d 's') # remove 's' presses from the scanner 

    if [ "$choice" = "1" ]; then
        check_wifi_network

        check_permissions_setter "$settings_script_path" # Start Listener if desired

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
      check_wifi_network

      check_permissions_setter "$settings_script_path" # Start Listener if desired

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
      check_wifi_network

      check_permissions_setter "$settings_script_path" # Start Listener if desired

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
    
    elif [ "$choice" = "5" ]; then
      echo "Ok, making venv..."
      export LOCAL_VENV_DIR_PATH="$(python "$settings_script_path" LOCAL_VENV_DIR_PATH -s)"
      export LOCAL_VENV_REQUIREMENTS_FILE="$(python "$settings_script_path" LOCAL_VENV_REQUIREMENTS_FILE -s)"
      "$(python "$settings_script_path" MAKE_LOCAL_VENV_SCRIPT -s)"

      break
    elif [ "$choice" = "6" ]; then
      check_wifi_network
      echo "Ok, making SSH Keys ..."
      docker run -it --rm \
        -e CHID="$CHID" \
        -e SSH_DIRECTORY="$(python "$settings_script_path" docker SSH_DIRECTORY -s)" \
        -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
        -v "$(python "$settings_script_path" LOCAL_SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
        --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
        meghanwalsh/nfb_docker:latest \
        "$(python "$settings_script_path" docker MAKE_LOCAL_SSH_KEYS -s)"
      break
    
    elif [ "$choice" = "7" ]; then
      check_wifi_network

      check_permissions_setter "$settings_script_path" # Start Listener if desired

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
        -e ROI_MASK_DIR_PATH="$(python "$settings_script_path" ROI_MASK_DIR_PATH -s)" \
        -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
        -v "$(python "$settings_script_path" LOCAL_SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
        --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
        meghanwalsh/nfb_docker:latest \
        "$(python "$settings_script_path" docker OLD_REGISTER_EASYREG_SCRIPT -s)"

      break
    else
      echo "Please choose a valid number option'"
    fi

  done
}
function activate_venv { 
  settings_script_path="$1"

  CONDA_INSTALLATION_SCRIPT=$(python "$settings_script_path" LOCAL_CONDA_INSTALLATION_SCRIPT -s)
  source "$CONDA_INSTALLATION_SCRIPT"

  LOCAL_VENV_DIR_PATH=$(python "$settings_script_path" LOCAL_VENV_DIR_PATH -s)

  if [ -d "$LOCAL_VENV_DIR_PATH" ]; then 
    echo "Found the needed local Conda environment at ${LOCAL_VENV_DIR_PATH}. Activating it..."
    conda activate "$LOCAL_VENV_DIR_PATH"
    echo "Using env: ${CONDA_DEFAULT_ENV}"
  else
    echo "Could not activate the local_venv"
  fi
    
}

echo "Running the Neurofeedback Task Executor Script. If prompted to enter a password below, type your computer password."
sudo -v 

echo ""
echo "Setup Information:"
# get settings path and user file path 
settings_script_path="$(dirname $(dirname "$(realpath "$0")"))/tasks_run/scripts/settings.py"
script_dir=$(dirname "$settings_script_path")
user_file=$(python "$settings_script_path" USERS_FILE -s)

check_access "$settings_script_path"
registered_info "$user_file"
check_for_priv_key "$settings_script_path"
networksetup -getairportnetwork en0


echo " "
echo "Your Registered Information: "
echo "User: $USER"
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
  choice=$(echo "$choice" | tr -d 's') # remove 's' presses from the scanner 

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

    check_permissions_setter "$settings_script_path" # Start Listener if desired

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

    check_permissions_setter "$settings_script_path" # Start Listener if desired

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

    check_permissions_setter "$settings_script_path" # Start Listener if desired

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

    check_permissions_setter "$settings_script_path" # Start Listener if desired

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

    activate_venv "$settings_script_path"

    check_permissions_setter "$settings_script_path" # Start Listener if desired

    echo "Setting up environment variables needed ..."
    export LOCAL_SAMBASHARE_DIR="$(python "$settings_script_path" LOCAL_SAMBASHARE_DIR_PATH -s)"
    export TMP_OUTDIR_PATH="$(python "$settings_script_path" TMP_OUTDIR_PATH -s)"
    export MNI_BRAIN_PATH="$(python "$settings_script_path" MNI_BRAIN_PATH -s)"
    export MNI_ACC_MASK_PATH="$(python "$settings_script_path" MNI_ACC_MASK_PATH -s)"
    export MNI_MOTOR_MASK_PATH="$(python "$settings_script_path" MNI_MOTOR_MASK_PATH -s)"
    export MNI_RIFG_MASK_PATH="$(python "$settings_script_path" MNI_RIFG_MASK_PATH -s)"
    export ROI_MASK_DIR_PATH="$(python "$settings_script_path" ROI_MASK_DIR_PATH -s)"
    
    
    echo "Calling script ..."
    "$(python "$settings_script_path" REGISTER_FNIRT_SCRIPT -s)"

    break
  
  elif [ "$choice" = "7" ]; then
    echo "Ok, Running EASYREG Localizer..."

    check_wifi_network

    check_permissions_setter "$settings_script_path" # Start Listener if desired

    docker run -it --rm \
      -e CHID="$CHID" \
      -e USER="$USER" \
      -e TZ="$(python "$settings_script_path" TZ -s)" \
      -e DOCKER_SSH_PRIVATE_KEY_PATH="$(python "$settings_script_path" docker LOCAL_PATH_TO_PRIVATE_KEY -s)" \
      -e E3_PRIVATE_KEY_PATH="$(python "$settings_script_path" docker E3_PRIVATE_KEY_PATH -s)" \
      -e E3_HOSTNAME="$(python "$settings_script_path" E3_HOSTNAME -s)" \
      -e E3_PATH_TO_SETTINGS="$(python "$settings_script_path" E3_PATH_TO_SETTINGS -s)" \
      -e E3_SETUP_REG_AND_COMPUTE_PATH="$(python "$settings_script_path" E3_SETUP_REG_AND_COMPUTE_PATH -s)" \
      -e LOCAL_MASK_DIR_PATH="$(python "$settings_script_path" ROI_MASK_DIR_PATH -s)" \
      -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
      -v "$(python "$settings_script_path" LOCAL_SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
      --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
      meghanwalsh/nfb_docker:latest \
      "$(python "$settings_script_path" docker REGISTER_EASYREG_SCRIPT -s)" 
    break
    


  elif [ "$choice" = "8" ]; then
    echo "Ok, Running Functional Localizer ..."

    activate_venv "$settings_script_path"

    check_permissions_setter "$settings_script_path" # Start Listener if desired
    
    python "$(python "$settings_script_path" LOCALIZER_SCRIPT -s)"
    break

  elif [ "$choice" = "9" ]; then
    run_utility_scripts "$CHID" "$settings_script_path"
    break
  else
     echo "Please choose '1', '2', '3', '4','5', '6', '7', '8' or '9'"
  fi
done