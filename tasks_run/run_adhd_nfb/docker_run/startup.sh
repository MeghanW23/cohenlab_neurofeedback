#!/bin/bash

set -e

echo " ----- RUNNING THE CONTAINER STARTUP SCRIPT NOW ----- "
echo "Sourcing the config script ... "
echo "config_script: $DOCKER_CONFIG_FILE_PATH"
source "$DOCKER_CONFIG_FILE_PATH"

echo "Path to inputted scripts and data directories: $DOCKER_DATA_AND_TASK_PATH"

# Run inputted scripts
if [[ "$1" == *.sh ]]; then
  echo "Running shell script ... "
  ./"$1"
elif [[ "$1" == *.py ]]; then
  echo "Running python script ..."
  python3 "$1"
else
  echo "Filetype of inputted script to run is unrecognized."
  exit 1
fi