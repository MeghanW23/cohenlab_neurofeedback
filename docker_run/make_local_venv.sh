#!/bin/bash

# script for installing necessary packages for running local scripts

set -e 


touch ~/.bash_profile
conda init bash
source ~/.bash_profile


# Check if variables are set
if [ -z "$LOCAL_VENV_DIR_PATH" ] || [ -z "$LOCAL_VENV_REQUIREMENTS_FILE" ]; then
  settings_path="$(dirname $(dirname $(realpath "$0")))/tasks_run/scripts/settings.py"
  echo "Getting variables LOCAL_VENV_DIR_PATH and LOCAL_VENV_REQUIREMENTS_FILE from: " 
  echo "$settings_path"

  LOCAL_VENV_REQUIREMENTS_FILE=$(python ${settings_path} LOCAL_VENV_REQUIREMENTS_FILE -s)
  LOCAL_VENV_DIR_PATH=$(python ${settings_path} LOCAL_VENV_DIR_PATH -s)
  echo "Input Paths: "
  echo "LOCAL_VENV_REQUIREMENTS_FILE: ${LOCAL_VENV_REQUIREMENTS_FILE}"
  echo "LOCAL_VENV_DIR_PATH: ${LOCAL_VENV_DIR_PATH}"
  
  if [ ! -f "$LOCAL_VENV_REQUIREMENTS_FILE" ]; then
    echo "LOCAL_VENV_REQUIREMENTS_FILE does not exist"
    exit 1
  fi


fi

# Create the conda environment
conda create --prefix "$LOCAL_VENV_DIR_PATH" python=3.10 -y

echo "Env Created. Activating..."
# Activate the environment
conda activate "$LOCAL_VENV_DIR_PATH"

echo "Installing TigerVNC..."
brew install tiger-vnc

# Install requirements
echo "Installing Python Packages from requirements file.."
pip install -r "$LOCAL_VENV_REQUIREMENTS_FILE"

echo "Installing dicom2niix..."
brew install dcm2niix

echo "All set! Please note that FSL will need to be installed manually through their website:"
echo "https://fsl.fmrib.ox.ac.uk/fsl/docs/#/" 

echo "To activate the virtual env, you can type: 'conda activate ${LOCAL_VENV_DIR_PATH}'"
echo "Tasks run soon after this conda installation may be especially slow. This is expected!"