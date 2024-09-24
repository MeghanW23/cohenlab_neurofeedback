#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

tarball_path="/workdir/venv.tar.gz"
output_venv="/workdir/venv"

echo "Creating Python virtual environment from tarball"

# Check if the tarball exists
if [ ! -f "$tarball_path" ]; then
  echo "Cannot find path to venv tarball. Attempting to pull from Google Drive using gdown"
  echo "Please download venv.tar.gz at google drive link:"
  echo "    https://drive.google.com/file/d/1xw_sj_ZfMsJcK1-j7QQmrwbUxx-kqAZd/view?usp=sharing    "
  echo "then run this script (./get_venv.sh) again."
fi

# Check if the tarball exists after the attempt to pull
if [ ! -f "$tarball_path" ]; then
  echo "Could not find tarball after pulling from Google Drive"
  exit 1
fi

# Extract the tarball
echo "Extracting tarball..."
tar -xzvf "$tarball_path" -C /workdir  # Specify the output directory for extraction

# Check if the virtual environment directory was created
if [ ! -d "$output_venv" ]; then
  echo "Could not create venv dir"
  exit 1  # Exit if the venv directory does not exist
else
  echo "venv creation successful."
  echo "To activate, type: venv"
fi
