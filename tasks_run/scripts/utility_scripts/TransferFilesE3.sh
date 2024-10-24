#!/bin/bash

set -e

echo "Using private_key at: ${DOCKER_SSH_PRIVATE_KEY_PATH}"
echo "Using hostname at: $E3_HOSTNAME"

# Check whether to push or pull
if [ "$1" == "push" ]; then
  echo "Script will push from local to e3"
elif [ "$1" == "pull" ]; then
  echo "Script will pull from e3 to local"
else
  echo "Please set positional argument 1 to either push or pull"
  exit 1
fi

# Check whether handling a directory or a file
if [ "$2" == "directory" ]; then
  echo "Script will $1 a directory"
elif [ "$2" == "file" ]; then
  echo "Script will $1 a file"
else
  echo "Please set positional argument 2 to either directory or file"
  exit 1
fi

path_to_local=""
while true; do
  read -p "Enter Path to Docker: " path_to_local
  # Check if the path exists
  if  [ ! -e "$path_to_local" ] && [ "$1" == "push" ]; then
    echo "Cannot find $path_to_local. Try again"
  else
    # Check if the path matches the expected type (directory or file)
    if [ "$1" == "push" ] && [ "$2" == "directory" ] && [ ! -d "$path_to_local" ]; then
      echo "The script was called to push a directory from Docker to e3, but the inputted Docker path is not a directory. Try again."
    elif [ "$1" == "push" ] && [ "$2" == "file" ] && [ ! -f "$path_to_local" ]; then
      echo "The script was called to push a file from Docker to e3, but the inputted Docker path is not a file. Try again."
    elif [ "$1" == "pull" ] && [ "$2" == "file" ] && [ ! -d "$path_to_local" ]; then
       echo "The script was called to pull a file to Docker from e3, but the inputted Docker path is not a directory. Try again."
    else
      echo "Ok, storing Docker path: $path_to_local"
      break  # Exit the loop if the path is valid
    fi
  fi
done

path_to_e3=""
while true; do
  read -p "Enter Remote Path to E3: " path_to_e3

  # Use SSH to check the existence of remote path
  if [ "$1" == "push" ] && [ "$2" == "directory" ]; then
    if ! ssh -i "$DOCKER_SSH_PRIVATE_KEY_PATH" "$CHID"@"$E3_HOSTNAME" "[ -d $path_to_e3 ]"  > /dev/null 2>&1; then
      echo "Remote directory does not exist. Try again."
    else
      echo "Ok, storing remote path: $path_to_e3"
      break
    fi
  elif [ "$1" == "push" ] && [ "$2" == "file" ]; then
    if ! ssh -i "$DOCKER_SSH_PRIVATE_KEY_PATH" "$CHID"@"$E3_HOSTNAME" "[ -d $path_to_e3 ]"  > /dev/null 2>&1; then
      echo "Remote directory does not exist. Try again."
    else
      echo "Ok, storing remote path: $path_to_e3"
      break
    fi
  elif [ "$1" == "pull" ] && [ "$2" == "directory" ]; then
    if ! ssh -i "$DOCKER_SSH_PRIVATE_KEY_PATH" "$CHID"@"$E3_HOSTNAME" "[ -d $path_to_e3 ]"  > /dev/null 2>&1; then
      echo "Remote directory does not exist. Try again."
    else
      echo "Ok, storing remote path: $path_to_e3"
      break
    fi
  elif [ "$1" == "pull" ] && [ "$2" == "file" ]; then
    if ! ssh -i "$DOCKER_SSH_PRIVATE_KEY_PATH" "$CHID"@"$E3_HOSTNAME" "[ -f $path_to_e3 ]"  > /dev/null 2>&1; then
      echo "Remote file does not exist. Check if the inputted path is a file. Try again."
    else
      echo "Ok, storing remote path: $path_to_e3"
      break
    fi
  fi
done

echo "Doing File Transfer... "

if [ "$1" == "push" ]; then
  if rsync -a -e "ssh -i $DOCKER_SSH_PRIVATE_KEY_PATH" "$path_to_local" "$CHID@$E3_HOSTNAME:$path_to_e3"; then
    echo "Successfully pushed $2 to $path_to_e3"
  else
    echo "Error pushing $2 to $path_to_e3"
    exit 1
  fi
else
  if rsync -a -e "ssh -i $DOCKER_SSH_PRIVATE_KEY_PATH" "$CHID@$E3_HOSTNAME:$path_to_e3" "$path_to_local"; then
    echo "Successfully pulled $2 from $path_to_e3"
  fi
fi