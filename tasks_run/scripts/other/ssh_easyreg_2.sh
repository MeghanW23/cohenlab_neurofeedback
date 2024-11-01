#!/bin/bash

set -e

function wait_for_new_dicom_dir {
    starting_directory_count="$(ls "${DOCKER_SAMBASHARE_DIR}" | wc -l)"
    
    while true; do
        current_directory_count="$(ls "${DOCKER_SAMBASHARE_DIR}" | wc -l)"
        
        if [ "$current_directory_count" -gt "$starting_directory_count" ]; then
            echo "${DOCKER_SAMBASHARE_DIR}/$(ls -tr "${DOCKER_SAMBASHARE_DIR}" | tail -n 1)"
            break
        else
            sleep 0.1
        fi
    done
}

function wait_for_dicoms {
  dicom_dir=$1
  while true; do 
    current_directory_count="$(ls "${dicom_dir}" | wc -l)"
    if [ "$current_directory_count" -gt 10 ]; then
      echo "Found 10 DICOMS in the directory. Starting registration now ..."
      break
    else
      current_directory_count="$(ls "${dicom_dir}" | wc -l)"
      sleep 0.1
    fi
  done
}


script_directory="$(dirname $(realpath "$0"))"
if [ ! -d "$script_directory" ]; then
    echo "Could not find script directory: ${script_directory}"
else
    echo "Found script directory: ${script_directory}"
fi


settings_script="${script_directory}/settings.py"
if [ ! -f "$settings_script" ]; then
    echo "Could not find settings file: ${settings_script}"
else
    echo "Found settings file: ${settings_script}"
fi

if [ -z "$DOCKER_SAMBASHARE_DIR" ]; then
    echo "Could not find env variable DOCKER_SAMBASHARE_DIR"
else
    echo "DOCKER_SAMBASHARE_DIR: ${DOCKER_SAMBASHARE_DIR}"
fi

settings_file="${script_directory}/settings.py"
if [ ! -f "$settings_script" ]; then
    echo "Could not find settings file: ${settings_file}"
else
    echo "Found settings file: ${settings_file}"
fi

if [ -z "$CHID" ]; then
    echo "Could not find env variable CHID"
else
    echo "CHID: ${CHID}"
    export CHID="$CHID"
fi

if [ -z "$USER" ]; then
    echo "Could not find env variable USER"
else
    echo "USER: ${USER}"
    export USER="$USER"
fi

if [ -z "$E3_INPUT_FUNC_DATA_DIR" ]; then
    echo "Could not find env variable E3_INPUT_FUNC_DATA_DIR"
else
    echo "E3_INPUT_FUNC_DATA_DIR: ${E3_INPUT_FUNC_DATA_DIR}"
    export E3_INPUT_FUNC_DATA_DIR="$E3_INPUT_FUNC_DATA_DIR"
fi

if [ -z "$PRIVATE_KEY_PATH" ]; then
    echo "Could not find env variable PRIVATE_KEY_PATH"
else
    echo "PRIVATE_KEY_PATH: ${PRIVATE_KEY_PATH}"
    export PRIVATE_KEY_PATH="$PRIVATE_KEY_PATH"
fi

if [ -z "$E3_HOSTNAME" ]; then
    echo "Could not find env variable E3_HOSTNAME"
else
    echo "E3_HOSTNAME: ${E3_HOSTNAME}"
    export E3_HOSTNAME="$E3_HOSTNAME"
fi

if [ -z "$E3_COMPUTE_PATH" ]; then
    echo "Could not find env variable E3_COMPUTE_PATH"
else
    echo "E3_COMPUTE_PATH: ${E3_COMPUTE_PATH}"
    export E3_COMPUTE_PATH="$E3_COMPUTE_PATH"
fi

if [ -z "$LOCAL_MASK_DIR_PATH" ]; then
    echo "Could not find env variable LOCAL_MASK_DIR_PATH"
else
    echo "LOCAL_MASK_DIR_PATH: ${LOCAL_MASK_DIR_PATH}"
    export LOCAL_MASK_DIR_PATH="$LOCAL_MASK_DIR_PATH"
fi


dicom_dir=" "
while true; do
  read -p "Wait for new sambashare directory or start automatically with the most recent dir? (wait/start) " wait_or_start
  if [[ "$wait_or_start" == "wait" ]]; then
    echo "Ok, waiting for new sambashare directory ..."
    dicom_dir=$(wait_for_new_dicom_dir)
    echo "Detected new dicom directory in the sambashare dir: ${dicom_dir}"
    echo "Waiting for 10 dicoms to be in the dir to run ..."
    wait_for_dicoms "$dicom_dir"

    break
  elif [[ "$wait_or_start" == "start" ]]; then
    echo "Ok, starting now ..."
    dicom_dir="${DOCKER_SAMBASHARE_DIR}/$(ls -tr ${DOCKER_SAMBASHARE_DIR} | tail -n 1)"
    echo "Using directory: ${dicom_dir}"        
    break
  else
    echo "Please enter either 'wait' or 'start'"
  fi
done


echo "Pushing Data to E3 and then logging in to e3..."
# rsync -a -e "ssh -i /workdir/.ssh/docker_e3_key_$CHID -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" "$three_dimensional_nifti_path" "$CHID@$E3_HOSTNAME:$E3_INPUT_FUNC_DATA_DIR"

# Capture the local username and use as an env var in e3
# export LOCAL_USER="$USER"
# echo "Sending env var USER: $LOCAL_USER"

# export LOCAL_MASK_DIR_PATH="$ROI_MASK_DIR_PATH"
# echo "Local project directory: ${LOCAL_MASK_DIR_PATH}"

# SSH into the remote server and set the USER variable to the local value
ssh -i "${PRIVATE_KEY_PATH}" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -t "${CHID}@${E3_HOSTNAME}" "export USER='${LOCAL_USER}' && export LOCAL_MASK_DIR_PATH='${LOCAL_MASK_DIR_PATH}' && ${E3_COMPUTE_PATH}"
