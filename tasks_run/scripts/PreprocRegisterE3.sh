#!/bin/bash

set -e

echo "This script performs preprocessing on task data before sending the output to e3 for roi mask registration"
# set func data dir on e3
path_to_e3="/lab-share/Neuro-Cohen-e2/Public/notebooks/mwalsh/registration/func_data"
# get the path to the sambashare and then the dicom dir
samba_dir=$(python -c "from settings import SAMBASHARE_DIR_PATH; print(SAMBASHARE_DIR_PATH)")
dicom_dir="${samba_dir}/$(ls -tr ${samba_dir} | tail -n 1)"
echo "--------------------------------------"
echo "Using most recent DICOM DIR: ${dicom_dir}"
echo "--------------------------------------"

# push unnecessary files to outdir
outdir=$(python -c "from settings import TMP_OUTDIR_PATH; print(TMP_OUTDIR_PATH)")
echo "Pushing outputted files to: ${outdir}"

echo "Running dcm2niix on the dicom dir ..."
dcm2niix -o "$outdir" "$dicom_dir"

echo "Cutting off first nifti slice ..."
output_nii_filename=$(ls -tr ${outdir} | grep -E 'nii|nii.gz' | tail -n 1)
output_nii_path="${outdir}/${output_nii_filename}"
three_dimensional_nifti_path="${outdir}/3d_nifti.nii.gz"
fslroi "$output_nii_path" "$three_dimensional_nifti_path" 0 -1 0 -1 0 -1 0 1

if rsync -a -e "ssh -i /workdir/.ssh/docker_e3_key_$CHID" "$three_dimensional_nifti_path" "$CHID@e3-login.tch.harvard.edu:$path_to_e3" > /dev/null 2>&1; then
  echo "Successfully pushed data to $path_to_e3"
else
  echo "Error pushing data to $path_to_e3"
  exit 1
fi

echo "To continue, please do the following steps: "
echo "(1) type 'e3'"
echo "(2) type 'compute2'"
echo "(3) type 'reg' followed by the roi mask you want to create (acc, motor, rifg)"