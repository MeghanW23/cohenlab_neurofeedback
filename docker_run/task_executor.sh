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
function check_git {
  settings_script_path="$1"
  GIT_DIR_PATH=$(python "$settings_script_path" GIT_DIR_PATH -s)
  PROJECT_DIRECTORY=$(python "$settings_script_path" PROJECT_DIRECTORY -s)

  if [ ! -d "$GIT_DIR_PATH" ]; then 
    echo "WARNING: Could not find file ${GIT_DIR_PATH} associated with variable: GIT_DIR_PATH"
    echo "Skipping git check ..." 
    return 1
  fi

  if [ ! -d "$PROJECT_DIRECTORY" ]; then 
    echo "WARNING: Could not find directory ${PROJECT_DIRECTORY} associated with variable: PROJECT_DIRECTORY"
    echo "Skipping git check ..." 
    return 1
  fi 

  git_result=$(git --git-dir="$GIT_DIR_PATH" --work-tree="$PROJECT_DIRECTORY" fetch) # for fetching even when script is called outside of local repo
  git_status=$? 
  if [ "$git_status" -eq 128 ]; then 
    echo "Issue with authentication and/or authorization connecting to GitHub. Are you connected to the internet?"
    read -p "Press 'enter' to continue. "
    return 0
  fi 

  commit_diff=$(git --git-dir="$GIT_DIR_PATH" --work-tree="$PROJECT_DIRECTORY" rev-list --count HEAD..origin/main)
  if [ -z "$commit_diff" ]; then
    echo "ERROR: Unable to compare branches. Is 'origin/main' available?"
    echo "Skipping git check ..." 
    return 1
  elif [ "$commit_diff" -eq 0 ]; then
    echo "Your branch is up to date with 'origin/main'"
  else
    echo " "
    echo "Your git branch is behind 'origin/main'."
    read -p "Press 'enter' to continue without updating your branch. Press 'x' and then 'enter' to end the script. " git_end_script
    if [ "$git_end_script" = "x" ]; then
      echo "Ok, ending script."
      exit 0
    else
      echo "Ok, continuing without updating..."
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
     return 0
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
  export settings_script_path="$settings_script_path"

  samba_ssh_priv_key=$(python "$settings_script_path" SAMBA_USER_PRIVATE_KEY_PATH -s)
  export samba_ssh_priv_key="$samba_ssh_priv_key"
  if [ ! -f "$samba_ssh_priv_key" ]; then 
    echo "SSH Private key for Samba_User SSH: ${samba_ssh_priv_key} does not exist"
    echo "To make sshing into samba_user from your current user passwordless, do 'See Utility Tasks' and then 'Make SSH Keys for Passwordless SSH from current user to samba_user'"
    read -p "Press any key to continue without SSH Keys " 
  fi 

  run_permissions_script=$(python "$settings_script_path" RUN_PERMISSIONS_SETTING_SCRIPT -s)
  if [ ! -f "$run_permissions_script" ]; then 
    echo "Script to Run Permissions Setting Script: ${run_permissions_script} does not exist"
    exit 1
  fi 

  
  run_permissions_script=$(python "$settings_script_path" RUN_PERMISSIONS_SETTING_SCRIPT -s)
  if [ ! -f "$run_permissions_script" ]; then 
    echo "Script to Run Permissions Setting Script: ${run_permissions_script} does not exist"
    exit 1
  fi 
  
  permissions_script=$(python "$settings_script_path" PERMISSIONS_SETTING_SCRIPT -s)
  export permissions_script="$permissions_script" # so its acessable by run_permissions_script, if started
  if [ ! -f "$permissions_script" ]; then 
    echo "Permissions-setting script: ${permissions_script} was not found."
    exit 1
  fi 
  
  nohup_log_file=$(python "$settings_script_path" NOHUP_LOG_FILE -s)
  export nohup_log_file="$nohup_log_file" # so its acessable by run_permissions_script, if started
  
  process_id_textfile=$(python "$settings_script_path" PROCESS_ID_TEXTFILE -s)
  export process_id_textfile="$process_id_textfile" # so its acessable by run_permissions_script, if started
  if [ ! -f "$process_id_textfile" ]; then 
    echo "Process ID Storing Textfile: ${process_id_textfile} was not found."
    echo "Creating it now ..."
    touch "$process_id_textfile"
  fi
  PID="$(cat $process_id_textfile)"
  if [ -z "$PID" ]; then 
    echo "Process ID associated with permissions-setting script was not found. I will assume the permissions-setting script is not running."
    while true; do
      read -p "Start running the permission-setting script? (y/n): " run_perm_setter
      if [ "$run_perm_setter" = "y" ]; then 
        echo "Ok, starting up the permission-setting script now ..."
        "$run_permissions_script"
        break
      elif [ "$run_perm_setter" = "n" ]; then
        echo "Ok, continuing without permission setting..."
        sleep 0.2 # to allow experimenter to read above words before continuing 
        break
      else
        echo "Please enter either 'y' or 'n'. Try again. "
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
}
function run_utility_scripts {
  CHID="$1"
  settings_script_path="$2"

  echo -e "\nUtility Tasks: "
  echo "(1) Transfer Files to/from E3"
  echo "(2) Run ClearDirs.py"
  echo "(3) Go to E3"
  echo "(4) Compare E3 settings file to local"
  echo "(5) Make a Virtual Environment via Conda to Run Scripts Locally"
  echo "(6) Make SSH Keys for Passwordless SSH from Local to E3"
  echo "(7) Run Old Localizer"
  echo "(8) Manage Permission-Setting Process"
  echo "(9) Make SSH Keys for Passwordless SSH from current user to samba_user"
  echo "(10) See After Scan Scripts"
  echo "(11) Go Back to Main Options"
  echo " " 

  while true; do
    read -p "Please enter the number corresponding with the utility task you want to run: " choice
    choice=$(echo "$choice" | tr -d 's') # remove 's' presses from the scanner 

    if [ "$choice" = "1" ]; then
      check_wifi_network

      # check_permissions_setter "$settings_script_path" # Start Listener if desired

      docker run -it --rm \
        -e CHID="$CHID" \
        -e TZ="$(python "$settings_script_path" TZ -s)" \
        -e DOCKER_SSH_PRIVATE_KEY_PATH="$(python "$settings_script_path" docker LOCAL_PATH_TO_PRIVATE_KEY -s)" \
        -e E3_HOSTNAME="$(python "$settings_script_path" E3_HOSTNAME -s)" \
        -e TRANSFER_FILES_SCRIPT="$(python "$settings_script_path" docker TRANSFER_FILES_SCRIPT -s)" \
        -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
        -v "$(python "$settings_script_path" SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
        --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
        meghanwalsh/nfb_docker:latest \
        "$(python "$settings_script_path" docker TRANSFER_FILES_SCRIPT -s)"

      # manage_permissions_process "$settings_script_path"

      break

    elif [ "$choice" = "2" ]; then
      echo "Ok, Running the Clear Directory Script ..."
      check_wifi_network

      # check_permissions_setter "$settings_script_path" # Start Listener if desired

      docker run -it --rm \
        -e CHID="$CHID" \
        -e TZ="$(python "$settings_script_path" TZ -s)" \
        -e PRIVATE_KEY_PATH="$(python "$settings_script_path" docker LOCAL_PATH_TO_PRIVATE_KEY -s)" \
        -e E3_HOSTNAME="$(python "$settings_script_path" E3_HOSTNAME -s)" \
        -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
        -v "$(python "$settings_script_path" SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
        --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
        meghanwalsh/nfb_docker:latest \
        "$(python "$settings_script_path" docker CLEAR_DIRS_SCRIPT -s)"

      # manage_permissions_process "$settings_script_path"

      break
    elif [ "$choice" = "3" ]; then
      echo "Ok, ssh-ing into e3 ..."
      check_wifi_network

      # check_permissions_setter "$settings_script_path" # Start Listener if desired

      docker run -it --rm \
        -e CHID="$CHID" \
        -e TZ="$(python "$settings_script_path" TZ -s)" \
        -e DOCKER_SSH_PRIVATE_KEY_PATH="$(python "$settings_script_path" docker LOCAL_PATH_TO_PRIVATE_KEY -s)" \
        -e E3_HOSTNAME="$(python "$settings_script_path" E3_HOSTNAME -s)" \
        -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
        -v "$(python "$settings_script_path" SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
        --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
        meghanwalsh/nfb_docker:latest \
        "$(python "$settings_script_path" docker SSH_COMMAND_SCRIPT -s)" \

      # manage_permissions_process "$settings_script_path"

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
        -v "$(python "$settings_script_path" SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
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
        -v "$(python "$settings_script_path" SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
        --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
        meghanwalsh/nfb_docker:latest \
        "$(python "$settings_script_path" docker MAKE_LOCAL_SSH_KEYS -s)"
      break
    
    elif [ "$choice" = "7" ]; then
      check_wifi_network

      # check_permissions_setter "$settings_script_path" # Start Listener if desired

      echo "Registering MNI Space Mask to Subject Space Via Easyreg"
      docker run -it --rm \
        -e CHID="$CHID" \
        -e USER="$USER" \
        -e TZ="$(python "$settings_script_path" TZ -s)" \
        -e LOCAL_SAMBASHARE_DIR_PATH="$(python "$settings_script_path" SAMBASHARE_DIR_PATH -s)" \
        -e E3_HOSTNAME="$(python "$settings_script_path" E3_HOSTNAME -s)" \
        -e E3_INPUT_FUNC_DATA_DIR="$(python "$settings_script_path" E3_PATH_TO_INPUT_FUNC_DATA -s)" \
        -e PRIVATE_KEY_PATH="$(python "$settings_script_path" docker LOCAL_PATH_TO_PRIVATE_KEY -s)" \
        -e E3_COMPUTE_PATH="$(python "$settings_script_path" E3_COMPUTE_PATH -s)" \
        -e TMP_OUTDIR_PATH="$(python "$settings_script_path" docker TMP_OUTDIR_PATH -s)" \
        -e E3_PATH_TO_OUTPUT_MASK="$(python "$settings_script_path" E3_PATH_TO_OUTPUT_MASK -s)" \
        -e ROI_MASK_DIR_PATH="$(python "$settings_script_path" ROI_MASK_DIR_PATH -s)" \
        -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
        --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
        meghanwalsh/nfb_docker:latest \
        "$(python "$settings_script_path" docker OLD_REGISTER_EASYREG_SCRIPT -s)"
      
      # manage_permissions_process "$settings_script_path"

      break    
    elif [ "$choice" = "8" ]; then
      echo "Starting manager..." 
      manage_permissions_process "$settings_script_path"
      while true; do 
        read -p "Run another permission-setting action? (y/n): " run_again
        if [ "$run_again" = "y" ]; then 
          echo "Ok, running again..."
          manage_permissions_process "$settings_script_path"
        elif [ "$run_again" = "n" ]; then 
          echo "Ok, exiting..."
          break
        else
          echo "Please enter 'y' or 'n'"
        fi 
      done 
      break 

    elif [ "$choice" = "9" ]; then
      MAKE_SAMBA_USER_SSH_KEYS="$(python "$settings_script_path" MAKE_SAMBA_USER_SSH_KEYS -s)"
      export SSH_DIRECTORY="$(python "$settings_script_path" SSH_DIRECTORY -s)"
      if [ ! -f "$MAKE_SAMBA_USER_SSH_KEYS" ]; then
        echo "Could not find script to make Samba_User ssh keys at: ${MAKE_SAMBA_USER_SSH_KEYS}"
        exit 1
      else
        "$MAKE_SAMBA_USER_SSH_KEYS"
      fi 

      break

    elif [ "$choice" = "10" ]; then
      run_after_scan_scripts "$CHID" "$settings_script_path"
      status=$?
      if [ "$status" = 1 ]; then
        echo "Showing utility options again..."
      else
        break
      fi
    elif [ "$choice" = "11" ]; then
      return 1
    else
      echo "Please choose a valid number option"
    fi
  done
}
function run_after_scan_scripts {
  CHID="$1"
  settings_script_path="$2"

  echo -e "\nAfter Scan Tasks: "
  echo "(1) Run Log Analysis"
  echo "(2) Calculate rIFG ISI Drift"
  echo "(3) Package Session Data and Send to E3"
  echo "(4) Run fMRIPrep"
  echo "(5) Go Back to Utility Scripts"
  echo ""

  while true; do
    read -p "Please enter the number corresponding with the after scan task you want to run: " choice
    choice=$(echo "$choice" | tr -d 's')

    if [ "$choice" = "1" ]; then
      echo "Running Log Analysis..."
      docker run -it --rm \
        -p 5999:5999 \
        -e DISPLAY=:99 \
        -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
        -v "$(python "$settings_script_path" SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
        --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
        meghanwalsh/nfb_docker:latest \
        "$(python "$settings_script_path" docker OUTPUT_LOG_ANALYSIS_SCRIPT -s)" "$settings_script_path" "$monitor_width" "$monitor_height" "$(python "$settings_script_path" docker VNC_X11_LOG_PATH -s)" "$(python "$settings_script_path" docker VNC_XVFB_LOG_PATH -s)"
      break

    elif [ "$choice" = "2" ]; then
      echo "Calculating ISI Drift..."
      docker run -it --rm \
        -p 5999:5999 \
        -e DISPLAY=:99 \
        -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
        -v "$(python "$settings_script_path" SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
        --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
        meghanwalsh/nfb_docker:latest \
        "$(python "$settings_script_path" docker ISI_DRIFT_CALCULATION_SCRIPT -s)" "$settings_script_path" "$monitor_width" "$monitor_height" "$(python "$settings_script_path" docker VNC_X11_LOG_PATH -s)" "$(python "$settings_script_path" docker VNC_XVFB_LOG_PATH -s)"
      break

    elif [ "$choice" = "3" ]; then
      python "$(python "$settings_script_path" PACKAGE_SUBJECT_DATA_SCRIPT -s)"
      break

    elif [ "$choice" = "4" ]; then
      echo "Starting fMRIPrep process..."
      docker run -it --rm \
        -p 5999:5999 \
        -e DISPLAY=:99 \
        -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
        -v "$(python "$settings_script_path" SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
        --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
        meghanwalsh/nfb_docker:latest \
        "$(python "$settings_script_path" docker RUN_FMRIPREP_SCRIPT -s)" "$settings_script_path" "$monitor_width" "$monitor_height" "$(python "$settings_script_path" docker VNC_X11_LOG_PATH -s)" "$(python "$settings_script_path" docker VNC_XVFB_LOG_PATH -s)"
      break

    elif [ "$choice" = "5" ]; then
      run_utility_scripts "$CHID" "$settings_script_path"
      break
    fi
  done
}
function activate_venv { 
  settings_script_path="$1"

  CONDA_INSTALLATION_SCRIPT=$(python "$settings_script_path" LOCAL_CONDA_INSTALLATION_SCRIPT -s)
  source "$CONDA_INSTALLATION_SCRIPT"
  

  LOCAL_VENV_DIR_PATH=$(python "$settings_script_path" LOCAL_VENV_DIR_PATH -s)

  if [ -d "$LOCAL_VENV_DIR_PATH" ]; then 
    if [ "$CONDA_DEFAULT_ENV" != "base" ] && [[ "$CONDA_DEFAULT_ENV" != *"local_venv"* ]]; then 
      echo "Deactivating current env."
      conda deactivate
    fi

    # echo "Found the needed local Conda environment at ${LOCAL_VENV_DIR_PATH}. Activating it..."
    conda activate "$LOCAL_VENV_DIR_PATH"
    echo "Using env: ${CONDA_DEFAULT_ENV}"
  else
    echo "Could find the path to the local_venv."
    echo "Run: 'Make a Virtual Environment via Conda to Run Scripts Locally' Under 'See Utility Tasks' if you have not created the local_venv." 
    read -p "To attempt the task directly on host system or env already running, press enter. " host_system_task
  fi
    
}
manage_permissions_process() {
  settings_script_path="$1"

  echo "Checking if the permissions-setting script is running..."

  # Get Paths and Process ID 
  samba_ssh_priv_key=$(python "$settings_script_path" SAMBA_USER_PRIVATE_KEY_PATH -s)
  export samba_ssh_priv_key="$samba_ssh_priv_key"
  if [ ! -f "$samba_ssh_priv_key" ]; then 
    echo "SSH Private key for Samba_User SSH: ${samba_ssh_priv_key} does not exist"
    echo "To make sshing into samba_user from your current user passwordless, do 'See Utility Tasks' and then 'Make SSH Keys for Passwordless SSH from current user to samba_user'"
  fi 

  run_permissions_script=$(python "$settings_script_path" RUN_PERMISSIONS_SETTING_SCRIPT -s)
  if [ ! -f "$run_permissions_script" ]; then 
    echo "Script to Run Permissions Setting Script: ${run_permissions_script} does not exist"
    read -p "Press any key to continue without SSH Keys " 
  fi 

  permissions_script=$(python "$settings_script_path" PERMISSIONS_SETTING_SCRIPT -s)
  export permissions_script="$permissions_script"
  if [ ! -f "$permissions_script" ]; then 
    echo "Permissions-setting script: ${permissions_script} does not exist."
    exit 1
  fi 

  nohup_log_file=$(python "$settings_script_path" NOHUP_LOG_FILE -s)
  export nohup_log_file="$nohup_log_file"
  if [ ! -f "$nohup_log_file" ]; then 
    echo "Creating Log file ..."
    touch "$nohup_log_file"
    # Consider removing the exit if you want the script to continue
    exit 1
  fi 

  process_id_textfile=$(python "$settings_script_path" PROCESS_ID_TEXTFILE -s)
  export process_id_textfile="$process_id_textfile"
  if [ ! -f "$process_id_textfile" ]; then 
    echo "Process ID Storing Textfile: ${process_id_textfile} does not exist."
    echo "Creating it now ..."
    touch "$process_id_textfile"
  else
    PID="$(cat "$process_id_textfile")"
    if sudo kill -0 "$PID" 2>/dev/null; then
      echo "Permissions-setting script is running."

      while true; do
        read -p "Kill running permission-setting process? (y/n): " kill_process
        if [ "$kill_process" = "y" ]; then 
          echo "Ok, killing the process now..."
          sudo kill "$(cat "$process_id_textfile")"
          echo "Process is killed."
          break
        elif [ "$kill_process" = "n" ]; then 
          echo "Ok, leaving process running."
          echo "To kill later, you can run: "
          echo " "
          echo "    sudo kill \$(cat \"$process_id_textfile\")"
          echo " "
          break
        else
          echo "Please enter either 'y' or 'n'"
        fi
      done

      if [ "$kill_process" = "n" ]; then
        while true; do
          read -p "Head and Tail Script Log (Last 10 Lines)? (y/n): " tail_log
          if [ "$tail_log" = "y" ]; then 
            echo "Ok, tailing permissions script ..."
            if [ ! -f "$nohup_log_file" ]; then  
              echo "Could not find the nohup file: ${nohup_log_file}"
              exit 1
            else
              echo " " 
              echo "First 10 lines: "
              echo "----------------------"
              head "$nohup_log_file"
              echo "----------------------"
              echo " " 
              echo "Last 10 lines: "
              echo "----------------------"
              tail "$nohup_log_file"
              echo "----------------------"
              echo " " 
              break
            fi
          elif [ "$tail_log" = "n" ]; then 
            while true; do 
              read -p "Tail continuously? (y/n): " tail_continuous
              if [ "$tail_continuous" = "y" ]; then 
                echo "Ok, tailing continuously ..."
                echo "Press 'control' + 'c' to exit"
                sleep 0.1
                tail -f "$nohup_log_file"
                break
              elif [ "$tail_continuous" = "n" ]; then 
                echo "Ok, will not tail continuously..."
                break
              else
                echo "Please enter either 'y' or 'n'"
              fi 
            done 
            break
          else
            echo "Please enter either 'y' or 'n'"
          fi
        done
      fi
    else
      echo "Permission-settings script is not currently running."
      while true; do
        read -p "Start running the permission-setting script? (y/n): " run_perm_setter
        if [ "$run_perm_setter" = "y" ]; then 
          echo "Ok, starting up the permission-setting script now ..."
          if [ -x "$run_permissions_script" ]; then
            "$run_permissions_script"
          else
            echo "Error: $run_permissions_script is not executable."
            exit 1
          fi
          break
        elif [ "$run_perm_setter" = "n" ]; then
          echo "Ok, permission-setting script will not be run."

          while true; do 
            read -p "See head and tail of last run's log script? (y/n): " tail_and_head_last
            if [ "$tail_and_head_last" = "y" ]; then 
              echo "Ok, printing out head and tail of last run's log script: " 
              echo " " 
              echo "First 10 lines: "
              echo "----------------------"
              head "$nohup_log_file"
              echo "----------------------"
              echo " " 
              echo "Last 10 lines: "
              echo "----------------------"
              tail "$nohup_log_file"
              echo "----------------------"
              echo " "
              break
            elif [ "$tail_and_head_last" = "n" ]; then 
              echo "Ok, not printing out head and tail of last run's log script." 
              break 
            else
              echo "Please enter either 'y' or 'n'"
            fi 
          done

          break
        else
          echo "Please enter either 'y' or 'n'. Try again. "
        fi 
      done
    fi
  fi
}
function manage_samba_server() {
  settings_script_path="$1"
  automatic_version="$2"

  SAMBA_DOCKER_BOOT_SCRIPT=$(python "$settings_script_path" SAMBA_DOCKER_BOOT_SCRIPT -s)
  
  if [ ! -f ${SAMBA_DOCKER_BOOT_SCRIPT} ]; then 
    echo "Samba file server boot script: ${SAMBA_DOCKER_BOOT_SCRIPT} could not be found." 
    read -p "Press any key to continue withoot booting the samba file server." 
  else 
    if [ "$automatic_version" = "true" ]; then 
      "${SAMBA_DOCKER_BOOT_SCRIPT}" "$settings_script_path" "$automatic_version"
    else
      "${SAMBA_DOCKER_BOOT_SCRIPT}" "$settings_script_path"
    fi 

    
  fi 
}
function check_rest_duration() {
  settings_script_path="$1"
  task="$2"
  if [ "$task" == "rifg" ] || [ "$task" == "msit" ]; then 
    REST_DURATION=$(python "$settings_script_path" REST_DURATION -s)

    if [ "$REST_DURATION" != 30 ]; then 
      echo " "
      echo "WARNING: Currently set rest duration is ${REST_DURATION}s and the expected rest duration is 30s"
      read -p "Press any key to continue. " rest_continue
    fi 
  fi

  if [ "$task" == "nfb" ]; then 
    START_REST_TRIAL=$(python "$settings_script_path" START_REST_TRIAL -s)
    if [ "$START_REST_TRIAL" != 1 ]; then 
      echo " "
      echo "WARNING: Currently set START_REST_TRIAL is ${START_REST_TRIAL} and the expected START_REST_TRIAL is 1"
      read -p "Press any key to continue. " rest_continue
    fi 

    START_NF_TRIAL=$(python "$settings_script_path" START_NF_TRIAL -s)
    if [ "$START_NF_TRIAL" != 20 ]; then 
      echo " "
      echo "WARNING: Currently set START_NF_TRIAL is ${START_NF_TRIAL} and the expected START_NF_TRIAL is 20"
      read -p "Press any key to continue. " rest_continue
    fi 

    EVEN_BLOCK_START_2ND_REST=$(python "$settings_script_path" EVEN_BLOCK_START_2ND_REST -s)
    if [ "$EVEN_BLOCK_START_2ND_REST" != 141 ]; then 
      echo " "
      echo "WARNING: Currently set EVEN_BLOCK_START_2ND_REST is ${EVEN_BLOCK_START_2ND_REST} and the expected EVEN_BLOCK_START_2ND_REST is 141"
      read -p "Press any key to continue. " rest_continue
    fi 

  fi 
}
function run_gui() {
  settings_script_path="$1"
  USER="$2"
  monitor_width="$3"
  monitor_height="$4"
  monitor_y_offset="$5"
  skip_asking="$6"

  port_info=$(netstat -an | grep 5998  | grep -i listen)

  # only ask to open GUI if 5998 is empty
  if [ -z "$port_info" ]; then 

    if [[ "$skip_asking" == "dont_skip" ]]; then 

      while true; do

        read -p "Would you like to open the Task Tracker GUI? (y/n): " open_gui
        if [ "$open_gui" == "y" ]; then 
          $(python "$settings_script_path" GUI_DOCKER_RUN_COMMAND -s) "$settings_script_path" "$USER" "$monitor_width" "$monitor_height" "$monitor_y_offset"
          echo "View the GUI by opening your VNC Viewer and connecting to: 'localhost:5998'"
          break 
        elif [ "$open_gui" == "n" ]; then 
          break
        else 
          echo "Please enter 'y' or 'n'."
        fi

      done 

    else
      $(python "$settings_script_path" GUI_DOCKER_RUN_COMMAND -s) "$settings_script_path" "$USER" "$monitor_width" "$monitor_height" "$monitor_y_offset"
      echo "View the GUI by opening your VNC Viewer and connecting to: 'localhost:5998'"
    fi

  else 
    echo "Task tracker is already running on port 5998."
    echo "View the GUI by opening your VNC Viewer and connecting to: 'localhost:5998'"
  fi
}
function start_vnc_viewer_wait() {
  settings_script_path="$1"
  port="$2"

  OPEN_VIEWER_SCRIPT="$(python "$settings_script_path" OPEN_VIEWER_SCRIPT -s)" 
  OPEN_VIEWER_SCRIPT_LOG="$(python "$settings_script_path" OPEN_VIEWER_SCRIPT_LOG -s)" 

  "$OPEN_VIEWER_SCRIPT" "$settings_script_path" "$port" > "$OPEN_VIEWER_SCRIPT_LOG" 2>&1 &
}
echo "Running the Neurofeedback Task Executor Script. If prompted to enter a password below, type your computer password."
sudo -v 

echo ""
echo "Setup Information:"
# get settings path and user file path 
settings_script_path="$(dirname $(dirname "$(realpath "$0")"))/tasks_run/scripts/settings.py"
script_dir=$(dirname "$settings_script_path")
user_file=$(python "$settings_script_path" USERS_FILE -s)

activate_venv "$settings_script_path"
check_access "$settings_script_path"
registered_info "$user_file"
check_for_priv_key "$settings_script_path"
networksetup -getairportnetwork en0
check_git "$settings_script_path"
manage_samba_server "$settings_script_path" "true"

# setup screen
monitor_info_script=$(python "$settings_script_path" MONITOR_INFO_SCRIPT -s)
printed_monitor_info=$(python "$monitor_info_script")
monitor_width="$(echo "$printed_monitor_info" | grep "Using Target Monitor Width" | cut -d ':' -f2 | tr -d '[:space:]')"
monitor_height="$(echo "$printed_monitor_info" | grep "Using Target Monitor Height" | cut -d ':' -f2 | tr -d '[:space:]')"
echo "Target Monitor Width: $monitor_width"
echo "Target Monitor Height: $monitor_height"

# Extract Target Monitor Y-Offset if it exists
monitor_y_offset=$(echo "$printed_monitor_info" | grep -o "Target Monitor Y-Offset: -*[0-9]\+")

# Check if Y-Offset was found
using_2nd_monitor=false
if [ -n "$monitor_y_offset" ]; then
    echo "$monitor_y_offset"
    using_2nd_monitor=true
else
    echo "Target Monitor Y-Offset not found"
    read -p "WARNING: Second monitor not detected. Press 'enter' to continue. " continue_1monitor
    monitor_y_offset="0"
fi

echo " "
echo "Your Registered Information: "
echo "User: $USER"
echo "Childrens ID: $CHID"

while true; do
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
  echo "(9) Manage Samba File Server"
  echo "(10) Start GUI"
  echo "(11) Open MRI Screen Viewer"
  echo "(12) See Utility Tasks"
  echo " "
  read -p "Please enter the number corresponding with the task you want to run: " choice
  choice=$(echo "$choice" | tr -d 's') # remove 's' presses from the scanner

  if [ "$choice" = "1" ]; then

    docker run -it --rm \
      -e TZ="$(python "$settings_script_path" TZ -s)" \
      -p 5999:5999 \
      -e DISPLAY=:99 \
      -e USER="$USER" \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
      -v "$(python "$settings_script_path" SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
      --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
      meghanwalsh/nfb_docker:latest \
      "$(python "$settings_script_path" docker TEST_PYGAME_SCRIPT -s)" "$settings_script_path" "$monitor_width" "$monitor_height" "$(python "$settings_script_path" docker VNC_X11_LOG_PATH -s)" "$(python "$settings_script_path" docker VNC_XVFB_LOG_PATH -s)"

    break

  elif [ "$choice" = "2" ]; then
    echo "Running RIFG Task ..."

    start_vnc_viewer_wait "$settings_script_path" 5999

    check_rest_duration "$settings_script_path" "rifg"

    run_gui "$settings_script_path" "$USER" "$monitor_width" "$monitor_height" "$monitor_y_offset" "dont_skip"

    docker run -it --rm \
      -p 5999:5999 \
      -e TZ="$(python "$settings_script_path" TZ -s)" \
      -e DISPLAY=:99 \
      -e USER="$USER" \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
      -v "$(python "$settings_script_path" SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
      --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
      meghanwalsh/nfb_docker:latest \
      "$(python "$settings_script_path" docker RIFG_TASK_SCRIPT -s)" "$settings_script_path" "$monitor_width" "$monitor_height" "$(python "$settings_script_path" docker VNC_X11_LOG_PATH -s)" "$(python "$settings_script_path" docker VNC_XVFB_LOG_PATH -s)"

    # manage_permissions_process "$settings_script_path"

    break

  elif [ "$choice" = "3" ]; then
    echo "Running MSIT Task ..."

    start_vnc_viewer_wait "$settings_script_path" 5999

    check_rest_duration "$settings_script_path" "msit"

    run_gui "$settings_script_path" "$USER" "$monitor_width" "$monitor_height" "$monitor_y_offset" "dont_skip"


    # check_permissions_setter "$settings_script_path" # Start Listener if desired

    docker run -it --rm \
      -p 5999:5999 \
      -e TZ="$(python "$settings_script_path" TZ -s)" \
      -e DISPLAY=:99 \
      -e USER="$USER" \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
      -v "$(python "$settings_script_path" SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
      --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
      meghanwalsh/nfb_docker:latest \
      "$(python "$settings_script_path" docker MSIT_TASK_SCRIPT -s)" "$settings_script_path" "$monitor_width" "$monitor_height" "$(python "$settings_script_path" docker VNC_X11_LOG_PATH -s)" "$(python "$settings_script_path" docker VNC_XVFB_LOG_PATH -s)"

    # manage_permissions_process "$settings_script_path"

    break

  elif [ "$choice" = "4" ]; then
    echo "Running Rest Task ..."

    start_vnc_viewer_wait "$settings_script_path" 5999

    run_gui "$settings_script_path" "$USER" "$monitor_width" "$monitor_height" "$monitor_y_offset" "dont_skip"


    # check_permissions_setter "$settings_script_path" # Start Listener if desired

    docker run -it --rm \
      -p 5999:5999 \
      -e TZ="$(python "$settings_script_path" TZ -s)" \
      -e DISPLAY=:99 \
      -e USER="$USER" \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
      -v "$(python "$settings_script_path" SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
      --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
      meghanwalsh/nfb_docker:latest \
      "$(python "$settings_script_path" docker REST_TASK_SCRIPT -s)" "$settings_script_path" "$monitor_width" "$monitor_height" "$(python "$settings_script_path" docker VNC_X11_LOG_PATH -s)" "$(python "$settings_script_path" docker VNC_XVFB_LOG_PATH -s)"

    # manage_permissions_process "$settings_script_path"

    break

  elif [ "$choice" = "5" ]; then
    echo "Running NFB Task ..."

    start_vnc_viewer_wait "$settings_script_path" 5999

    check_rest_duration "$settings_script_path" "nfb"

    run_gui "$settings_script_path" "$USER" "$monitor_width" "$monitor_height" "$monitor_y_offset" "dont_skip"


    # check_permissions_setter "$settings_script_path" # Start Listener if desired

    docker run -it --rm \
      -p 5999:5999 \
      -e TZ="$(python "$settings_script_path" TZ -s)" \
      -e DISPLAY=:99 \
      -e USER="$USER" \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
      -v "$(python "$settings_script_path" SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
      --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
      meghanwalsh/nfb_docker:latest \
      "$(python "$settings_script_path" docker NFB_TASK_SCRIPT -s)" "$settings_script_path" "$monitor_width" "$monitor_height" "$(python "$settings_script_path" docker VNC_X11_LOG_PATH -s)" "$(python "$settings_script_path" docker VNC_XVFB_LOG_PATH -s)"

    # manage_permissions_process "$settings_script_path"

    break

  elif [ "$choice" = "6" ]; then
    echo "Registering MNI Space Mask to Subject Space Via FNIRT/FNIRT"

    # check_permissions_setter "$settings_script_path" # Start Listener if desired

    echo "Setting up environment variables needed ..."
    export SAMBASHARE_DIR_PATH="$(python "$settings_script_path" SAMBASHARE_DIR_PATH -s)"
    export TMP_OUTDIR_PATH="$(python "$settings_script_path" TMP_OUTDIR_PATH -s)"
    export MNI_BRAIN_PATH="$(python "$settings_script_path" MNI_BRAIN_PATH -s)"
    export MNI_ACC_MASK_PATH="$(python "$settings_script_path" MNI_ACC_MASK_PATH -s)"
    export MNI_MOTOR_MASK_PATH="$(python "$settings_script_path" MNI_MOTOR_MASK_PATH -s)"
    export MNI_RIFG_MASK_PATH="$(python "$settings_script_path" MNI_RIFG_MASK_PATH -s)"
    export ROI_MASK_DIR_PATH="$(python "$settings_script_path" ROI_MASK_DIR_PATH -s)"


    echo "Calling script ..."
    "$(python "$settings_script_path" REGISTER_FNIRT_SCRIPT -s)" "$(python "$settings_script_path" PID_LIST_FILE -s)" 

    # manage_permissions_process "$settings_script_path"

    break

  elif [ "$choice" = "7" ]; then
    echo "Ok, Running EASYREG Localizer..."

    check_wifi_network


    # check_permissions_setter "$settings_script_path" # Start Listener if desired

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
      -e LOCAL_SAMBASHARE_DIR_PATH="$(python "$settings_script_path" SAMBASHARE_DIR_PATH -s)" \
      -e PID_LIST_FILE="$(python "$settings_script_path" docker PID_LIST_FILE -s)" \
      -v "$(python "$settings_script_path" PROJECT_DIRECTORY -s)":"$(python "$settings_script_path" docker PROJECT_DIRECTORY -s)" \
      -v "$(python "$settings_script_path" SAMBASHARE_DIR_PATH -s)":"$(python "$settings_script_path" docker SAMBASHARE_DIR_PATH -s)" \
      --entrypoint "$(python "$settings_script_path" docker DOCKER_PATH_TO_STARTUP_SCRIPT -s)" \
      meghanwalsh/nfb_docker:latest \
      "$(python "$settings_script_path" docker REGISTER_EASYREG_SCRIPT -s)"

    # manage_permissions_process "$settings_script_path"

    break



  elif [ "$choice" = "8" ]; then
    echo "Ok, Running Functional Localizer ..."


    # check_permissions_setter "$settings_script_path" # Start Listener if desired

    python "$(python "$settings_script_path" LOCALIZER_SCRIPT -s)"

    # manage_permissions_process "$settings_script_path"

    break

  elif [ "$choice" = "9" ]; then
    echo "Ok, Booting samba file server now ..."

    manage_samba_server "$settings_script_path"

    break

  elif [ "$choice" = "10" ]; then
    run_gui "$settings_script_path" "$USER" "$monitor_width" "$monitor_height" "$monitor_y_offset" "skip"
    break


  elif [ "$choice" = "11" ]; then

    if [[ "$using_2nd_monitor" == false ]]; then 
      echo "You must be connected to a second monitor to run this script."
    else
      # split y offset string 
      monitor_y_offset=$(echo "$monitor_y_offset" | awk '{print $NF}')

      python "$(python "$settings_script_path" MRI_VIEWER_SCRIPT -s)" &
    fi 

    break 

  elif [ "$choice" = "12" ]; then
    run_utility_scripts "$CHID" "$settings_script_path"
    status=$?
    if [ "$status" = 1 ]; then
      echo "Showing main options again..."
    else
      break
    fi

  else
     echo "Please choose a valid number option."
  fi
done