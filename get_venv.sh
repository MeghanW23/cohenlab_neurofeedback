#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status
tarball_path="/workdir/venv.tar.gz"
output_venv="/workdir/venv"

echo "Creating Python virtual environment from tarball"

# Check if the tarball exists
if [ ! -f "$tarball_path" ]; then
  echo "Cannot find path to venv tarball. Attempting to pull from Google Drive using gdown"

  # Use the correct Google Drive URL format
  command_output=$(gdown --no-cookies "https://drive.google.com/uc?id=1tLkdwqhbE40BLnxVN37rU2ku7VlQFZEZ" -O "$tarball_path")

  # Check if the command was successful
  if [ $? -eq 0 ]; then
    echo "Successful Pull:"
    echo "$command_output"
  else
    echo "Command failed."
    exit 1  # Exit if the pull command fails
  fi
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
fi
