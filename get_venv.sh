#!/bin/bash

tarball_path="/workdir/venv.tar.gz"
echo "Creating python virtual environment from tarball"
if [ ! -d "$tarball_path" ]; then
  echo "Cannot find path to venv tarball. Attempting to pull from google drive using gdown"
  command_output=$(gdown --no-cookies "https://drive.google.com/file/d/1tLkdwqhbE40BLnxVN37rU2ku7VlQFZEZ/view?usp=sharing" -O venv.tar.gz)
  # Check if the command was successful
  if [ $? -eq 0 ]; then
    echo "$command_output"
    echo "Successful Pull:"
  else
    echo "Command failed."
  fi
  if [ ! -d "$tarball_path" ]; then
    echo "Could not find tarball after pulling from gdrive"
    exit 1
  else
    tar -xzvf venv.tar.gz
  fi
else
  tar -xzvf venv.tar.gz
fi


