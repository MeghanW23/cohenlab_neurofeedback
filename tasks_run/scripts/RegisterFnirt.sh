#!/bin/bash

echo "Registering ROI mask to participant data via local fnirt script"

set -e

start_time=$(date +%s)
echo "Fnirt registration start time: $(date +"%Y-%m-%d %H:%M:%S")"

# get most recent dicom dir
samba_dir=$(python -c "from settings import SAMBASHARE_DIR_PATH; print(SAMBASHARE_DIR_PATH)")
dicom_dir="${samba_dir}/$(ls -tr ${samba_dir} | tail -n 1)"
echo "--------------------------------------"
echo "Using most recent DICOM DIR: ${dicom_dir}"
echo "--------------------------------------"

# push unnecessary files to outdir
outdir=$(python -c "from settings import TMP_OUTDIR_PATH; print(TMP_OUTDIR_PATH)")
echo "Pushing outputted files to: ${outdir}"

# get mni brain
mni_brain=$(python -c "from settings import MNI_BRAIN_PATH; print(MNI_BRAIN_PATH)")
echo "Path to MNI Brain: ${mni_brain}"

# get mni roi mask via experimenter input
while true; do
  echo "What ROI Mask Would You Like to Register? "
  echo "(1) ACC Mask"
  echo "(2) Motor Mask"
  echo "(3) RIFG Mask"

  read -p "Enter '1', '2', or '3': " choice

  if [ $choice = "1" ]; then
    echo "Ok, Registering ACC Mask"
    roi_mask=$(python -c "from settings import MNI_ACC_MASK_PATH; print(MNI_ACC_MASK_PATH)")
    echo "Using MNI ACC Mask at: $roi_mask"
    mask_type="acc"
    break

  elif [ $choice = "2" ]; then
    echo "Ok, Registering Motor Mask"
    roi_mask=$(python -c "from settings import MNI_MOTOR_MASK_PATH; print(MNI_MOTOR_MASK_PATH)")
    echo "Using MNI Motor Mask at: $roi_mask"
    mask_type="motor"
    break

  elif [ $choice = "3" ]; then
    echo "Ok, Registering RIFG Mask"
    roi_mask=$(python -c "from settings import MNI_RIFG_MASK_PATH; print(MNI_RIFG_MASK_PATH)")
    echo "Using MNI RIFG Mask at: $roi_mask"
    mask_type="rifg"
    break

  else
    echo "Please choose either 1, 2, or 3"
  fi
done

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

timestamp=$(date +"%Y%m%d_%H%M%S")

output_registered_brain_parent_dir=$(python -c "from settings import ROI_MASK_DIR_PATH; print(ROI_MASK_DIR_PATH)")
output_registered_brain="${output_registered_brain_parent_dir}/${pid}_fnirt_registered_${mask_type}_mask_${timestamp}"


echo "Running dcm2niix on the dicom dir ..."
dcm2niix -o "$outdir" "$dicom_dir"

echo "Cutting off first nifti slice ..."
output_nii_filename=$(ls -tr ${outdir} | grep -E 'nii|nii.gz' | tail -n 1)
output_nii_path="${outdir}/${output_nii_filename}"
three_dimensional_nifti_path="${outdir}/3d_nifti.nii.gz"
fslroi "$output_nii_path" "$three_dimensional_nifti_path" 0 -1 0 -1 0 -1 0 1

echo "Skull-stripping the brain ..."
ss_three_dimensional_nifti_path="${outdir}/ss_3d_nifti.nii.gz"
bet "$three_dimensional_nifti_path" "$ss_three_dimensional_nifti_path"

echo "Creating reference brain mask ..."
func_three_dimensional_mask="${outdir}/func_3d_brain_mask_nifti.nii.gz"
fslmaths "$ss_three_dimensional_nifti_path" -bin "$func_three_dimensional_mask"

echo "Running Flirt ..."
affine_matrix="${outdir}/affine_transform.mat"
flirt \
-ref "$three_dimensional_nifti_path" \
-in "$mni_brain" \
-omat "$affine_matrix" \
-out "${outdir}/affine_mni.nii.gz"


echo "Applying Flirt ..."
flirt \
-ref "$three_dimensional_nifti_path" \
-in "$roi_mask" \
-applyxfm \
-interp nearestneighbour \
-init "$affine_matrix" \
-out "${outdir}/affine_roi_mask.nii.gz"

echo "Running Fnirt ..."
nonlinear_matrix="${outdir}/nonlinear_transform.mat"
fnirt \
--ref="$three_dimensional_nifti_path" \
--in="$mni_brain" \
--refmask="$func_three_dimensional_mask" \
--aff="$affine_matrix" \
--cout="$nonlinear_matrix" \
--iout="${outdir}/nonlinear_mni.nii.gz"

echo "Applying Fnirt ..."
applywarp  \
--ref="$three_dimensional_nifti_path" \
--in="$roi_mask" \
--interp=nn \
--warp="$nonlinear_matrix" \
--out="$output_registered_brain"

end_time=$(date +%s)
echo "Total Time: $(("$end_time" - "$start_time"))"
echo "Registration Complete. Output Mask at: ${output_registered_brain}"