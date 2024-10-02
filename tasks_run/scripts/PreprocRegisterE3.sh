#!/bin/bash

set -e

echo "This script performs preprocessing on task data before sending the output to e3 for roi mask registration"
# get the path to the sambashare and then the dicom dir
samba_dir=$(python -c "from settings import SAMBASHARE_DIR_PATH; print(SAMBASHARE_DIR_PATH)")
dicom_dir="${samba_dir}/$(ls -tr ${samba_dir} | tail -n 1)"
echo "--------------------------------------"
echo "Using most recent DICOM DIR: ${dicom_dir}"
echo "--------------------------------------"

# get e3 hostname, the remote path to push output data to, and the e3 script to start compute node
e3_hostname=$(python -c "from settings import E3_HOSTNAME; print(E3_HOSTNAME)")
echo "Using hostname: ${e3_hostname}"

path_to_e3=$(python -c "from settings import PATH_TO_E3_INPUT_FUNC_DATA; print(PATH_TO_E3_INPUT_FUNC_DATA)")
echo "Sending output data to e3 path: ${path_to_e3}"

e3_compute_script_path=$(python -c "from settings import E3_COMPUTE_EASYREG_SCRIPT_PATH; print(E3_COMPUTE_EASYREG_SCRIPT_PATH)")
echo "Running e3 compute node via ${e3_compute_script_path}"

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
# push unnecessary files to outdir
outdir=$(python -c "from settings import TMP_OUTDIR_PATH; print(TMP_OUTDIR_PATH)")
echo "Pushing outputted files to: ${outdir}"

echo "Running dcm2niix on the dicom dir ..."
dcm2niix -o "$outdir" "$dicom_dir"

echo "Cutting off first nifti slice ..."
output_nii_filename=$(ls -tr ${outdir} | grep -E 'nii|nii.gz' | tail -n 1)
output_nii_path="${outdir}/${output_nii_filename}"

three_dimensional_nifti_filename="${pid}_3d_func_slice_$(date +"%Y%m%d_%H%M%S").nii.gz"
three_dimensional_nifti_path="${outdir}/${three_dimensional_nifti_filename}"
fslroi "$output_nii_path" "$three_dimensional_nifti_path" 0 -1 0 -1 0 -1 0 1

echo "Pushing Data to E3 ..."
rsync -a -e "ssh -i /workdir/.ssh/docker_e3_key_$CHID" "$three_dimensional_nifti_path" "$CHID"@"$e3_hostname":"$path_to_e3"

#source /lab-share/Neuro-Cohen-e2/Public/notebooks/mwalsh/registration/materials/store_ip_and_compute_srun.sh

echo "ssh ${CHID}@${e3_hostname}"
ssh ${CHID}@${e3_hostname}


ssh
echo "To continue, please do the following steps: "
echo "(1) type 'e3'"
echo "(2) type 'compute2'"
echo "(3) type 'reg' followed by the roi mask you want to create (acc, motor, rifg)"