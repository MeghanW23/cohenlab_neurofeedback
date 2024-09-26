#!/bin/bash

echo "Registering ROI mask to participant data via local fnirt script"

set -e

# get most recent dicom dir
samba_dir=$(python -c "from settings import SAMBASHARE_DIR_PATH; print(SAMBASHARE_DIR_PATH)")
dicom_dir="${samba_dir}/$(ls -tr ${samba_dir} | tail -n 1)"
echo "Using Most Recent DICOM DIR: ${dicom_dir}"

# push unnecessary files to outdir
outdir=$(python -c "from settings import TMP_OUTDIR_PATH; print(TMP_OUTDIR_PATH)")
echo "Pushing outputted files to: ${outdir}"

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

    break
  elif [ $choice = "2" ]; then
    echo "Ok, Registering Motor Mask"
    roi_mask=$(python -c "from settings import MNI_MOTOR_MASK_PATH; print(MNI_MOTOR_MASK_PATH)")
    echo "Using MNI Motor Mask at: $roi_mask"
    break

  elif [ $choice = "3" ]; then
    echo "Ok, Registering RIFG Mask"
    roi_mask=$(python -c "from settings import MNI_RIFG_MASK_PATH; print(MNI_RIFG_MASK_PATH)")
    echo "Using MNI RIFG Mask at: $roi_mask"
    break

  else
    echo "Please choose either 1, 2, or 3"
  fi
done

echo "Running dcm2niix on the dicom dir"
dcm2niix -o "$outdir" "$dicom_dir"

echo "Cutting off first nifti slice ..."
output_nii_path=$(ls -tr ${outdir} | grep -E 'nii|nii.gz' | tail -n 1)
three_dimensional_nifti_path="${outdir}/3d_nifti"
fslroi "$output_nii_path", "$three_dimensional_nifti_path" 0 -1 0 -1 0 -1 0 1

echo "Skull-stripping the brain ..."
ss_three_dimensional_nifti_path="${outdir}/ss_3d_nifti"
bet "$three_dimensional_nifti_path" "$ss_three_dimensional_nifti_path"

echo "Creating reference brain mask ..."
func_three_dimensional_mask="${outdir}/func_3d_brain_mask_nifti"
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
applywarp \
--ref="$three_dimensional_nifti_path" \
--in="$roi_mask" \
--interp==nn \
--warp="$nonlinear_matrix" \
--out=