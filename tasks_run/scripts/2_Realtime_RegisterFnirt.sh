#!/bin/bash

set -e

function wait_for_new_dicom_dir {
    starting_directory_count="$(ls "${SAMBASHARE_DIR_PATH}" | wc -l)"
    
    while true; do
        current_directory_count="$(ls "${SAMBASHARE_DIR_PATH}" | wc -l)"
        
        if [ "$current_directory_count" -gt "$starting_directory_count" ]; then
            echo "${SAMBASHARE_DIR_PATH}/$(ls -tr "${SAMBASHARE_DIR_PATH}" | tail -n 1)"
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
      sleep 1
      break
    else
      current_directory_count="$(ls "${dicom_dir}" | wc -l)"
      sleep 0.1
    fi
  done
}


echo "Registering ROI mask to participant data via fnirt script run locally."

# get and validate PID 
PID_LIST_FILE="$1"

while true 
do
    # input the pid 
    read -p "Enter Participant ID: " pid

    pid=$(echo "$pid" | xargs | tr '[:upper:]' '[:lower:]') # trim leading and trailing spaces

    # validate the PID format
    if [[ ! "$pid" =~ ^p[0-9]{3}$ ]]; then
        echo "Invalid Participant ID format. It must start with 'p' followed by three digits (e.g., p001)."
        continue
    fi

    # read pid list line by line
    found_pid=false
    if [[ -f "$PID_LIST_FILE" ]]; then
        while IFS= read -r line || [[ -n "$line" ]]; do
            # trim leading and trailing spaces
            line=$(echo "$line" | xargs)

            # skip empty lines
            if [[ -z "$line" ]]; then
                continue
            fi

            if [[ "$pid" == "$line" ]]; then
                found_pid=true
            fi

        done < "$PID_LIST_FILE"
    else
        echo "File $PID_LIST_FILE does not exist. Continuing with manual entry only."
    fi

    if [ "$pid" == "p999" ]; then 
        echo "Using Testing Participant ID ${pid}"
        break
    elif [[ "$found_pid" == false ]]; then
        echo "Using New Participant ID: ${pid}"

        # write PID to list 
        echo "" >> "$PID_LIST_FILE"
        echo "$pid" >> "$PID_LIST_FILE"

        break
    else
        get_new_pid=false

        echo "Found Already Existing Participant ID: ${pid}"
        while true 
        do 
            echo "Select from the following options:"
            echo "(1) Get a New Participant ID - NEW PARTICIPANTS ONLY"
            echo "(2) Using the Testing ID p999"
            echo "(3) Continue With the Already Existing Participant ID - CONTINUING PARTICIPANTS ONLY"
            read -p "Select an Option (1/2/3): " option

            # Validate input
            if [[ "$option" == "1" ]]; then 
                get_new_pid=true
                break 

            elif [[ "$option" == "2" ]]; then 
                pid="p999"
                break

            elif [[ "$option" == "3" ]]; then 
                break
            else

                echo "Please enter either 1, 2, or 3"
            fi 
        done 
        
        if [[ "$get_new_pid" == false ]]; then 
            break
        fi
    fi
done

echo "Using Participant ID: ${pid}"

# get mni roi mask via experimenter input
while true; do
  echo "What ROI Mask Would You Like to Register? "
  echo "(1) ACC Mask"
  echo "(2) Motor Mask"
  echo "(3) RIFG Mask"

  read -p "Enter '1', '2', or '3': " choice

  if [ $choice = "1" ]; then
    echo "Ok, Registering ACC Mask"
    roi_mask="$MNI_ACC_MASK_PATH"
    echo "Using MNI ACC Mask at: $roi_mask"
    mask_type="acc"
    break

  elif [ $choice = "2" ]; then
    echo "Ok, Registering Motor Mask"
    roi_mask="$MNI_MOTOR_MASK_PATH"
    echo "Using MNI Motor Mask at: $roi_mask"
    mask_type="motor"
    break

  elif [ $choice = "3" ]; then
    echo "Ok, Registering RIFG Mask"
    roi_mask=$MNI_RIFG_MASK_PATH
    echo "Using MNI RIFG Mask at: $roi_mask"
    mask_type="rifg"
    break

  else
    echo "Please choose either 1, 2, or 3"
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
    dicom_dir="${SAMBASHARE_DIR_PATH}/$(ls -tr ${SAMBASHARE_DIR_PATH} | tail -n 1)"
    echo "Using directory: ${dicom_dir}"        
    break
  else
    echo "Please enter either 'wait' or 'start'"
  fi
done

start_time=$(date +%s)
echo "Fnirt registration start time: $(date +"%Y-%m-%d %H:%M:%S")"

# get most recent dicom dir
if [ -z "$SAMBASHARE_DIR_PATH" ]; then
  echo "Could not find env variable for sambashare dir path SAMBASHARE_DIR_PATH"
  exit 1
fi
# dicom_dir="${SAMBASHARE_DIR_PATH}/$(ls -tr ${SAMBASHARE_DIR_PATH} | tail -n 1)"
echo "--------------------------------------"
echo "Using most recent DICOM DIR: ${dicom_dir}"
echo "--------------------------------------"

# push unnecessary files to
echo "Pushing outputted files to: ${TMP_OUTDIR_PATH}"

# get mni brain
echo "Path to MNI Brain: ${MNI_BRAIN_PATH}"

timestamp=$(date +"%Y%m%d_%H%M%S")

non_bin_output_registered_brain="${TMP_OUTDIR_PATH}/non_bin_${pid}_fnirt_registered_${mask_type}_mask_${timestamp}"
output_registered_brain="${ROI_MASK_DIR_PATH}/${pid}_fnirt_registered_${mask_type}_mask_${timestamp}"

echo "Running dcm2niix on the dicom dir ..."
dcm2niix -o "$TMP_OUTDIR_PATH" "$dicom_dir"

echo "Cutting off first nifti slice ..."
output_nii_filename=$(ls -tr ${TMP_OUTDIR_PATH} | grep -E 'nii|nii.gz' | tail -n 1)
output_nii_path="${TMP_OUTDIR_PATH}/${output_nii_filename}"
three_dimensional_nifti_path="${TMP_OUTDIR_PATH}/3d_nifti.nii.gz"
fslroi "$output_nii_path" "$three_dimensional_nifti_path" 0 -1 0 -1 0 -1 0 1
if [ ! -f "$three_dimensional_nifti_path" ]; then 
  echo "Could not find created 3d_nifti file (after the command that was intended to create it) at: '$three_dimensional_nifti_path'"
  exit 1
fi 

echo "Skull-stripping the brain ..."
ss_three_dimensional_nifti_path="${TMP_OUTDIR_PATH}/ss_3d_nifti.nii.gz"
bet "$three_dimensional_nifti_path" "$ss_three_dimensional_nifti_path"

echo "Creating reference brain mask ..."
func_three_dimensional_mask="${TMP_OUTDIR_PATH}/func_3d_brain_mask_nifti.nii.gz"
fslmaths "$ss_three_dimensional_nifti_path" -bin "$func_three_dimensional_mask"

echo "Running Flirt ..."
affine_matrix="${TMP_OUTDIR_PATH}/affine_transform.mat"
flirt \
-ref "$ss_three_dimensional_nifti_path" \
-in "$MNI_BRAIN_PATH" \
-omat "$affine_matrix" \
-out "${TMP_OUTDIR_PATH}/affine_mni.nii.gz"


echo "Applying Flirt ..."
flirt \
-ref "$ss_three_dimensional_nifti_path" \
-in "$roi_mask" \
-applyxfm \
-interp nearestneighbour \
-init "$affine_matrix" \
-out "${TMP_OUTDIR_PATH}/affine_roi_mask.nii.gz"

echo "Running Fnirt ..."
nonlinear_matrix="${TMP_OUTDIR_PATH}/nonlinear_transform.mat"
fnirt \
--ref="$ss_three_dimensional_nifti_path" \
--in="$MNI_BRAIN_PATH" \
--refmask="$func_three_dimensional_mask" \
--aff="$affine_matrix" \
--cout="$nonlinear_matrix" \
--iout="${TMP_OUTDIR_PATH}/nonlinear_mni.nii.gz"

echo "Applying Fnirt ..."
applywarp  \
--ref="$ss_three_dimensional_nifti_path" \
--in="$roi_mask" \
--interp=nn \
--warp="$nonlinear_matrix" \
--out="$non_bin_output_registered_brain"

echo "Binarizing Mask"
fslmaths "$non_bin_output_registered_brain" -bin "$output_registered_brain"


end_time=$(date +%s)
echo "Total Time: $(($end_time - $start_time))s"
echo "Registration Complete. Output Mask at: ${output_registered_brain}"