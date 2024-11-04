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

warnings=0
if [ ! -d "$DOCKER_SAMBASHARE_DIR" ]; then
    echo "Could not find env variable DOCKER_SAMBASHARE_DIR or the path: '${DOCKER_SAMBASHARE_DIR}' does not exist"
    ((warnings++))
else
    echo "DOCKER_SAMBASHARE_DIR: ${DOCKER_SAMBASHARE_DIR}"
fi


if [ -z "$CHID" ]; then
    echo "Could not find env variable CHID"
    ((warnings++))
else
    echo "CHID: ${CHID}"
    export CHID="$CHID"
fi

if [ -z "$USER" ]; then
    echo "Could not find env variable USER"
    ((warnings++))
else
    echo "USER: ${USER}"
    export USER="$USER"
fi

if [ -z "$E3_PATH_TO_INPUT_DIRECTORIES" ]; then
    echo "Could not find env variable E3_PATH_TO_INPUT_DIRECTORIES"
    ((warnings++))
else
    echo "E3_PATH_TO_INPUT_DIRECTORIES: ${E3_PATH_TO_INPUT_DIRECTORIES}"
    export E3_PATH_TO_INPUT_DIRECTORIES="$E3_PATH_TO_INPUT_DIRECTORIES"
fi

if [ ! -f "$PRIVATE_KEY" ]; then
    echo "Could not find env variable PRIVATE_KEY or the path: '${PRIVATE_KEY}' does not exist"
    ((warnings++))
else
    echo "PRIVATE_KEY: ${PRIVATE_KEY}"
    export PRIVATE_KEY="$PRIVATE_KEY"
fi

if [ -z "$E3_HOSTNAME" ]; then
    echo "Could not find env variable E3_HOSTNAME"
    ((warnings++))
else
    echo "E3_HOSTNAME: ${E3_HOSTNAME}"
    export E3_HOSTNAME="$E3_HOSTNAME"
fi

if [ -z "$E3_COMPUTE_PATH" ]; then
    echo "Could not find env variable E3_COMPUTE_PATH"
    ((warnings++))
else
    echo "E3_COMPUTE_PATH: ${E3_COMPUTE_PATH}"
    export E3_COMPUTE_PATH="$E3_COMPUTE_PATH"
fi

if [ ! -d "$ROI_MASK_DIR_PATH" ]; then
    echo "Could not find env variable ROI_MASK_DIR_PATH or the path: '${ROI_MASK_DIR_PATH}' does not exist"
    ((warnings++))
else
    echo "ROI_MASK_DIR_PATH: ${ROI_MASK_DIR_PATH}"
    export ROI_MASK_DIR_PATH="$ROI_MASK_DIR_PATH"
fi


if [ ! -d "$TMP_OUTDIR_PATH" ]; then
    echo "Could not find env variable TMP_OUTDIR_PATH or the path: '${TMP_OUTDIR_PATH}' does not exist"
    ((warnings++))
else
    echo "TMP_OUTDIR_PATH: ${TMP_OUTDIR_PATH}"
    export TMP_OUTDIR_PATH="$TMP_OUTDIR_PATH"
fi


if [ "$warnings" -gt 0 ]; then 
    echo "--------- CAUTION ---------"
    echo " Warnings rasied: ${warnings}"
    echo "--------- CAUTION ---------"
    read -p "Press any key to continue despite warnings. " continue_anyways

else
    echo "NO warnings raised. Continuing ..."
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
rsync -a -e "ssh -i /workdir/.ssh/docker_e3_key_$CHID -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" "$dicom_dir" "$CHID@$E3_HOSTNAME:$E3_PATH_TO_INPUT_DIRECTORIES"

# Capture the local username and use as an env var in e3
# export LOCAL_USER="$USER"
# echo "Sending env var USER: $LOCAL_USER"

# export LOCAL_MASK_DIR_PATH="$ROI_MASK_DIR_PATH"
# echo "Local project directory: ${LOCAL_MASK_DIR_PATH}"

# SSH into the remote server and set the USER variable to the local value
# ssh -i "${PRIVATE_KEY_PATH}" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -t "${CHID}@${E3_HOSTNAME}" "export USER='${LOCAL_USER}' && export LOCAL_MASK_DIR_PATH='${LOCAL_MASK_DIR_PATH}' && ${E3_COMPUTE_PATH}"
