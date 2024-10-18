#!/bin/bash

set -e

echo "This script performs preprocessing on task data before sending the output to e3 for roi mask registration"
# get the path to the sambashare and then the dicom dir
dicom_dir="${DOCKER_SAMBASHARE_DIR}/$(ls -tr ${DOCKER_SAMBASHARE_DIR} | tail -n 1)"
echo "--------------------------------------"
echo "Using most recent DICOM DIR: ${dicom_dir}"
echo "--------------------------------------"

echo "Using hostname: ${E3_HOSTNAME}"
echo "Sending output data to e3 path: ${E3_INPUT_FUNC_DATA_DIR}"
echo "Using private key at local path: ${PRIVATE_KEY_PATH}"
echo "Path to e3 compute script: ${E3_COMPUTE_PATH}"
echo "Pushing outputted files to: ${TMP_OUTDIR_PATH}" # push unnecessary files to outdir

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
rsync -a -e "ssh -i /workdir/.ssh/docker_e3_key_$CHID" "$three_dimensional_nifti_path" "$CHID"@"$E3_HOSTNAME":"$E3_INPUT_FUNC_DATA_DIR"

ssh -i "${PRIVATE_KEY_PATH}" -t "${CHID}@${E3_HOSTNAME}" "${E3_COMPUTE_PATH}"

# echo "Pulling data from E3 ..."
# rsync -a -e "ssh -i $PRIVATE_KEY_PATH" "$CHID@$E3_HOSTNAME:$E3_INPUT_FUNC_DATA_DIR" "$DOCKER_SUBJ_SPACE_MASK_DIR" > /dev/null 2>&1