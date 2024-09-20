#!/bin/bash

echo "Registering ROI mask to participant data via local fnirt script"

set -e

# get most recent dicom dir
samba_dir=$(python -c "from settings import SAMBASHARE_DIR_PATH; print(SAMBASHARE_DIR_PATH)")
dicom_dir="${samba_dir}/$(ls -tr ${samba_dir} | tail -n 1)"
echo "Using Most Recent DICOM DIR: ${dicom_dir}"

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

# push unneccessary files to outdir
outdir=$(python -c "from settings import TMP_OUTDIR_PATH; print(TMP_OUTDIR_PATH)")
echo "Pushing outputted files to: ${outdir}"

mni_brain=$(python -c "from settings import MNI_BRAIN_PATH; print(MNI_BRAIN_PATH)")
echo "Path to MNI Brain: ${mni_brain}"
#     subprocess.run(["fnirt", f"--ref={Func3dNii}", f"--in={MniBrain}", f"--refmask={Func3dMask}", f"--aff={outdir}/{pid}_affine_transform.mat", f"--cout={outdir}/{pid}_nonlinear_transform", f"--iout={outdir}/{pid}_MniBraininSubjSpace.nii.gz"])