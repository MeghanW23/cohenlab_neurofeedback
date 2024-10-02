#!/bin/bash

# Script to setup starting aliases and functions needed during container runtime

# list all commands
echo "alias commands='alias && declare -f'" >> ~/.bashrc

# got to home dir: /workdir
echo "alias home='cd /workdir/'" >> ~/.bashrc

# go to data directory
echo "alias data='cd /workdir/tasks_run/data/'" >> ~/.bashrc

# go to log directory
echo "alias logs='cd /workdir/tasks_run/data/logs'" >> ~/.bashrc

# go to script directory
echo "alias scripts='cd /workdir/tasks_run/scripts'" >> ~/.bashrc

# go to sambashare directory
echo "alias samba='cd /workdir/tasks_run/data/sambashare'" >> ~/.bashrc

# setup alias for passwordless ssh into e3
echo "alias e3='ssh -F /workdir/.ssh/config_${CHID} e3_${CHID}'" >> ~/.bashrc

# activate python virtual environment, if not activated during startup
echo "alias venv='source /workdir/venv/bin/activate'" >> ~/.bashrc

# simulate real-time mri data collection by copying a dicom to a target directory every RepetitionTime
echo "alias mock='python /workdir/tasks_run/scripts/other/mock_mri_file_production.py'" >> ~/.bashrc

# go to dicom directory called 'test_dir' used as the output dir for the mock alias
echo "alias testdir='cd /workdir/tasks_run/data/sambashare/test_dir'" >> ~/.bashrc

# clear dicom directory called 'test_dir' used as the output dir for the mock alias
echo "alias cleartestdir='rm -rf /workdir/tasks_run/data/sambashare/test_dir/*'" >> ~/.bashrc

 # run rifg task
echo "alias rifg='python /workdir/tasks_run/scripts/rifg_task.py'" >> ~/.bashrc

# run neurofeedback task
echo "alias nfb='python /workdir/tasks_run/scripts/nf_calc_MW.py'" >> ~/.bashrc

# run pre-neurofeedback msit task
echo "alias premsit='python /workdir/tasks_run/scripts/MSIT_NF_PRE.py'" >> ~/.bashrc

# run post-neurofeedback msit task
echo "alias postmsit='python /workdir/tasks_run/scripts/MSIT_NF_POST.py'" >> ~/.bashrc

# run localizer on subject-space mask
echo "alias localize='python /workdir/tasks_run/scripts/Localizer.py'" >> ~/.bashrc

# go through a list of specific directories and optionally clear out files and/or push them to e3
echo "alias cleandocker='python /workdir/tasks_run/scripts/ClearDirs.py'" >> ~/.bashrc

# transfer files to e3 using two parameters (1: do either push or pull, 2: select either file or directory)
echo "e3transfer() {
  return_here=\$(pwd)
  cd /workdir/tasks_run/scripts || echo 'Could not go to script directory: /workdir/tasks_run/scripts'
  ./TransferFilesE3.sh \"\$@\"
  cd \"\$return_here\" || echo 'Could not return to starting directory.'
}" >> ~/.bashrc


# shellcheck disable=SC2016
register_roi_function='
# Function to register ROI
register_roi () {
  error_message="Please specify which method you will use to register the ROI when calling the \047register_roi\047 function: \n Run either \047register_roi fnirt\047 or \047register_roi easyreg\047"
  script_type=$1
  if [ -z "$script_type" ]; then
    echo -e "${error_message}"
  else
    if [ "$script_type" = "fnirt" ]; then
      echo "Registering MNI ROI to subject space locally using Fnirt ..."
      return_here=$(pwd)
      cd /workdir/tasks_run/scripts || echo "Could not go to script directory: /workdir/tasks_run/scripts"
      ./RegisterFnirt.sh
      cd "$return_here" || echo "Could not return to starting directory."
    elif [ "$script_type" = "easyreg" ]; then
      echo "Registering MNI ROI to subject space on E3 using Easyreg ..."
      cd /workdir/tasks_run/scripts || echo "Could not go to script directory: /workdir/tasks_run/scripts"
      ./PreprocRegisterE3.sh
    else
      echo -e "${error_message}"
    fi
  fi
}
'
# Append the function to ~/.bashrc
echo "$register_roi_function" >> ~/.bashrc

source ~/.bashrc
