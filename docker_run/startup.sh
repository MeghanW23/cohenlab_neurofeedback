#!/bin/bash

function get_info_for_e3_transfer {
  local pushpull   # push or pull element from e3
  local dirfile    # transfer dir or file

  while true; do
    read -p "Are you downloading or uploading to E3? (push/pull): " pushpull
    if [ "$pushpull" = "pull" ]; then
      echo "Ok, downloading from e3"
      break
    elif [ "$pushpull" = "push" ]; then
      echo "Ok, uploading to e3"
      break
    else
      echo "Please type either 'push' or 'pull'. Try again."
    fi
  done

  while true; do
    read -p "Are you transferring a directory or file? (d/f): " dirfile
    if [ "$dirfile" = "d" ]; then
      echo "Ok, transferring directory ... "
      dirfile="directory"
      break
    elif [ "$dirfile" = "f" ]; then
      echo "Ok, transferring file ... "
      dirfile="file"
      break
    else
      echo "Please type either 'd' or 'u'. Try again."
    fi
  done

  "$E3TRANSFER_SCRIPT" "$pushpull" "$dirfile"
}

set -e

echo " ----- Running Startup Docker Script ... ----- "

# Validate if the first argument is provided
if [ -z "$1" ]; then
  echo "Error: No script specified to run."
  exit 1
fi

# run func if e3transfer
if [[ "$1" = "$E3TRANSFER_SCRIPT" ]]; then
  get_info_for_e3_transfer

# Check if the script is a shell script
elif [[ "$1" == *.sh ]]; then
  echo "e3 compute path: $E3_COMPUTE_PATH"
  echo "Running shell script: $1"
  "$1"

# Check if the script is a Python script
elif [[ "$1" == *.py ]]; then
  echo "Running Python script: $1"
  python3 "$1"

# Unrecognized file type
else
  echo "Error: Filetype of the inputted script '$1' is unrecognized. Must be a .sh or .py script."
  exit 1
fi
