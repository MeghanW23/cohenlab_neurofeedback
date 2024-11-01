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

echo "This script performs preprocessing on task data before sending the output to e3 for roi mask registration"

# get pid and timestamp, then use to make outputted registered subj-space mask path
while true; do
  read -p "Enter pid: " pid
  letter_count=$(echo "$pid" | tr -cd '[:alpha:]' | wc -c)
  expected_digits=$(echo "$pid" | tr -d 'Pp')

  if [ "$letter_count" -ne 1 ]; then
    echo "Please follow pid syntax: 'P' followed by digits"
  elif [[ ! "$pid" == *[Pp]* ]]; then
    echo "Please follow pid syntax: 'P' followed by digits"
  elif [[ ! "$expected_digits" =~ ^[0-9]+$ ]]; then
    echo "Please follow pid syntax: 'P' followed by digits"
  else
    echo "Ok, using pid: ${pid}"
    break
  fi
done


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

echo "--------------------------------------"
echo "Using most recent DICOM DIR: ${dicom_dir}"
echo "--------------------------------------"

echo "Using your username: ${USER}"
echo "Using hostname: ${E3_HOSTNAME}"
echo "Sending output data to e3 path: ${E3_INPUT_FUNC_DATA_DIR}"
echo "Using private key at local path: ${PRIVATE_KEY_PATH}"
echo "Path to e3 compute script: ${E3_COMPUTE_PATH}"
echo "Pushing outputted files to: ${TMP_OUTDIR_PATH}" # push unnecessary files to outdir
echo "Pulling created masks from: ${E3_PATH_TO_OUTPUT_MASK}"
echo "Pushing created masks to: ${ROI_MASK_DIR_PATH}"

echo "Running dcm2niix on the dicom dir ..."
dcm2niix -o "$TMP_OUTDIR_PATH" "$dicom_dir"

echo "Cutting off first nifti slice ..."
output_nii_filename=$(ls -tr ${TMP_OUTDIR_PATH} | grep -E 'nii|nii.gz' | tail -n 1)
output_nii_path="${TMP_OUTDIR_PATH}/${output_nii_filename}"

three_dimensional_nifti_filename="${pid}_3d_func_slice_$(date +"%Y%m%d_%H%M%S").nii.gz"
three_dimensional_nifti_path="${TMP_OUTDIR_PATH}/${three_dimensional_nifti_filename}"

# Using nilearn and nibabel to cut the first 3D slice (instead of fslroi "$output_nii_path" "$three_dimensional_nifti_path" 0 -1 0 -1 0 -1 0 1)
python3 - <<EOF
from nilearn import image
import nibabel as nib

# Define the file paths from the shell script
output_nii_path = "$output_nii_path"
three_dimensional_nifti_path = "$three_dimensional_nifti_path"

# Load the 4D image and extract the first 3D volume (slice)
first_slice = image.index_img(output_nii_path, 0)

# Save the extracted 3D slice to the output path
nib.save(first_slice, three_dimensional_nifti_path)
EOF

if [ $? -eq 0 ]; then
  echo "Successfully extracted and saved the first 3D slice to $three_dimensional_nifti_path"
else
  echo "Error: Failed to extract and save the 3D slice."
  exit 1
fi

echo "Pushing Data to E3 and then logging in to e3..."
rsync -a -e "ssh -i /workdir/.ssh/docker_e3_key_$CHID -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" "$three_dimensional_nifti_path" "$CHID@$E3_HOSTNAME:$E3_INPUT_FUNC_DATA_DIR"

# Capture the local username and use as an env var in e3
export LOCAL_USER="$USER"
echo "Sending env var USER: $LOCAL_USER"

export LOCAL_MASK_DIR_PATH="$ROI_MASK_DIR_PATH"
echo "Local project directory: ${LOCAL_MASK_DIR_PATH}"

# SSH into the remote server and set the USER variable to the local value
ssh -i "${PRIVATE_KEY_PATH}" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -t "${CHID}@${E3_HOSTNAME}" "export USER='${LOCAL_USER}' && export LOCAL_MASK_DIR_PATH='${LOCAL_MASK_DIR_PATH}' && ${E3_COMPUTE_PATH}"
