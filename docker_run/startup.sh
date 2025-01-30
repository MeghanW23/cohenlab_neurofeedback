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

  "$TRANSFER_FILES_SCRIPT" "$pushpull" "$dirfile"
}


set -e

echo " ----- Running Startup Docker Script ... ----- "
settings_script_path="$2"
screen_width="$3"
screen_height="$4"
VNC_XVFB_LOG_PATH="$5"
VNC_X11_LOG_PATH="$6"
if [ -z "${VNC_XVFB_LOG_PATH}" -o -z "${VNC_X11_LOG_PATH}" -o -z "${screen_width}" -o -z "${screen_height}" ]; then 
  echo "Display will not be rendered."
else 
  echo "Starting Display Server..."
  screen_params="${screen_width}x${screen_height}"
  echo "See Xvfb Log at: ${VNC_XVFB_LOG_PATH}"
  echo "See x11 Log at: ${VNC_X11_LOG_PATH}"

  Xvfb :99 -screen 0 "${screen_params}x16" > "$VNC_XVFB_LOG_PATH" 2>&1 &
  x11vnc -display :99 -geometry "$screen_params" -forever  -verbose -nopw -rfbport 5999 > "$VNC_X11_LOG_PATH" 2>&1 &
fi

# Validate if the first argument is provided
if [ -z "$1" ]; then
  echo "Error: No script specified to run."
  exit 1
fi

# run func if e3transfer
if [[ "$1" = "$TRANSFER_FILES_SCRIPT" ]]; then
  get_info_for_e3_transfer

# Check if the script is a shell script
elif [[ "$1" == *.sh ]]; then
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