#!/bin/bash

# script for installing necessary packages for running local scripts

set -e 

# Check if variables are set
if [ -z "$LOCAL_VENV_DIR_PATH" ] || [ -z "$LOCAL_VENV_REQUIREMENTS_FILE" ]; then
  echo "Error: Please set LOCAL_VENV_DIR_PATH and LOCAL_VENV_REQUIREMENTS_FILE before running this script."
  exit 1
fi

# Create the conda environment
conda create --prefix "$LOCAL_VENV_DIR_PATH" python=3.10 -y

# Activate the environment
source activate "$LOCAL_VENV_DIR_PATH"

# Install requirements
pip install -r "$LOCAL_VENV_REQUIREMENTS_FILE"

echo "All set! Please note that FSL will need to be downloaded manually through their website:"
echo "https://fsl.fmrib.ox.ac.uk/fsl/docs/#/" 

echo "To activate the virtual env, you can type: 'conda activate ${LOCAL_VENV_DIR_PATH}'"
