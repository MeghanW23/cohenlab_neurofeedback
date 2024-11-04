#!/bin/bash

set -e

function wait_for_new_dicom_dir {
    starting_directory_count=$(ls "${DOCKER_SAMBASHARE_DIR}" | wc -l)
    
    while true; do
        current_directory_count=$(ls "${DOCKER_SAMBASHARE_DIR}" | wc -l)
        
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
    current_file_count=$(ls "${dicom_dir}" | wc -l)
    if [ "$current_file_count" -gt 10 ]; then
      echo "Found 10 DICOMS in the directory. Starting registration now ..."
      break
    else
      sleep 0.1
    fi
  done
}

echo " "
echo " ------------------------------------------------------------------------ "
echo "STARTING EASYREG REGISTRATION STEP ONE: Collecting data and sending to e3."
echo " ------------------------------------------------------------------------ "
echo " "
# Initialize warnings
warnings=0

# Validate environment variables
for var in DOCKER_SAMBASHARE_DIR CHID USER E3_PATH_TO_INPUT_DIRECTORIES PRIVATE_KEY E3_HOSTNAME E3_REGISTRATION_STEP_ONE ROI_MASK_DIR_PATH TMP_OUTDIR_PATH; do
  if [ -z "${!var}" ] || { [ "$var" = "DOCKER_SAMBASHARE_DIR" ] || [ "$var" = "ROI_MASK_DIR_PATH" ] || [ "$var" = "TMP_OUTDIR_PATH" ] && [ ! -d "${!var}" ]; }; then
    echo "Could not find or access required env variable: ${var}"
    ((warnings++))
  else
    export $var="${!var}"
    echo "${var}: ${!var}"
  fi
done

# Check if warnings were raised
if [ "$warnings" -gt 0 ]; then 
    echo "--------- CAUTION ---------"
    echo " Warnings raised: ${warnings}"
    echo "--------- CAUTION ---------"
    read -p "Press any key to continue despite warnings. " continue_anyways
else
    echo "NO warnings raised. Continuing ..."
fi

# Wait for or select dicom directory
dicom_dir=""
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
    dicom_dir="${DOCKER_SAMBASHARE_DIR}/$(ls -tr "${DOCKER_SAMBASHARE_DIR}" | tail -n 1)"
    echo "Using directory: ${dicom_dir}"        
    break
  else
    echo "Please enter either 'wait' or 'start'"
  fi
done

echo "To register, we only need a few DICOMS. Grabbing the first 10 and pushing to e3 ..."
formatted_date=$(date +"%Y-%m-%d_%H-%M-%S")
ten_dcm_dir="${TMP_OUTDIR_PATH}/ten_dcm_dir_${formatted_date}"
if [ -d "$ten_dcm_dir" ]; then
  echo "Removing old directory contents ..."
  rm -rf ${ten_dcm_dir}/*

else
  mkdir "$ten_dcm_dir"
fi 

# Get the first 10 DICOM files from dicom_dir
dicoms_to_copy=($(ls "$dicom_dir"/*.dcm | head -n 10))  # Store the DICOM files in an array

# Loop through the array and copy each DICOM file to ten_dcm_dir
for dicom in "${dicoms_to_copy[@]}"; do
    echo "Copying $dicom to $ten_dcm_dir"
    cp "$dicom" "$ten_dcm_dir"
done


# Transfer data to E3 and log in
echo "Pushing Data to E3 ..."
rsync -a -e "ssh -i /workdir/.ssh/docker_e3_key_$CHID -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" "$ten_dcm_dir" "$CHID@$E3_HOSTNAME:$E3_PATH_TO_INPUT_DIRECTORIES"

echo "Logging in to E3 ..."
ssh -i "$PRIVATE_KEY" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -t "$CHID@$E3_HOSTNAME" "export USER='$USER' && export LOCAL_MASK_DIR_PATH='$ROI_MASK_DIR_PATH' && ${E3_REGISTRATION_STEP_ONE}"
