#!/bin/bash

set -e

private_key=$(python3 -c "from settings import LOCAL_PATH_TO_PRIVATE_KEY; print(LOCAL_PATH_TO_PRIVATE_KEY)")
echo "Using private_key at: $private_key"
hostname=$(python3 -c "from settings import E3_HOSTNAME; print(E3_HOSTNAME)")
echo "Using hostname at: $hostname"

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
  read -p "Enter Path to Local: " path_to_local
  # Check if the path exists
  if  [ ! -e "$path_to_local" ] && [ "$1" == "push" ]; then
    echo "Cannot find $path_to_local. Try again"
  else
    # Check if the path matches the expected type (directory or file)
    if [ "$1" == "push" ] && [ "$2" == "directory" ] && [ ! -d "$path_to_local" ]; then
      echo "The script was called to push a directory from local to e3, but the inputted local path is not a directory. Try again."
    elif [ "$1" == "push" ] && [ "$2" == "file" ] && [ ! -f "$path_to_local" ]; then
      echo "The script was called to push a file from local to e3, but the inputted local path is not a file. Try again."
    elif [ "$1" == "pull" ] && [ "$2" == "file" ] && [ ! -d "$path_to_local" ]; then
       echo "The script was called to pull a file to local from e3, but the inputted local path is not a directory. Try again."
    else
      echo "Ok, storing local path: $path_to_local"
      break  # Exit the loop if the path is valid
    fi
  fi
done

path_to_e3=""
while true; do
  read -p "Enter Remote Path to E3: " path_to_e3

  # Use SSH to check the existence of remote path
  if [ "$1" == "push" ] && [ "$2" == "directory" ]; then
    if ! ssh -i "$private_key" "$CHID"@"$hostname" "[ -d $path_to_e3 ]"  > /dev/null 2>&1; then
      echo "Remote directory does not exist. Try again."
    else
      echo "Ok, storing remote path: $path_to_e3"
      break
    fi
  elif [ "$1" == "push" ] && [ "$2" == "file" ]; then
    if ! ssh -i "$private_key" "$CHID"@"$hostname" "[ -d $path_to_e3 ]"  > /dev/null 2>&1; then
      echo "Remote directory does not exist. Try again."
    else
      echo "Ok, storing remote path: $path_to_e3"
      break
    fi
  elif [ "$1" == "pull" ] && [ "$2" == "directory" ]; then
    if ! ssh -i "$private_key" "$CHID"@"$hostname" "[ -d $path_to_e3 ]"  > /dev/null 2>&1; then
      echo "Remote directory does not exist. Try again."
    else
      echo "Ok, storing remote path: $path_to_e3"
      break
    fi
  elif [ "$1" == "pull" ] && [ "$2" == "file" ]; then
    if ! ssh -i "$private_key" "$CHID"@"$hostname" "[ -f $path_to_e3 ]"  > /dev/null 2>&1; then
      echo "Remote file does not exist. Check if the inputted path is a file. Try again."
    else
      echo "Ok, storing remote path: $path_to_e3"
      break
    fi
  fi
done

echo "Doing File Transfer... "

if [ "$1" == "push" ]; then
  if rsync -a -e "ssh -i $private_key" "$path_to_local" "$CHID@$hostname:$path_to_e3" > /dev/null 2>&1; then
    echo "Successfully pushed $2 to $path_to_e3"
  else
    echo "Error pushing $2 to $path_to_e3"
    exit 1
  fi
else
  if rsync -a -e "ssh -i $private_key" "$CHID@$hostname:$path_to_e3" "$path_to_local" > /dev/null 2>&1; then
    echo "Successfully pulled $2 from $path_to_e3"
  else
    echo "Error pulling $2 from $path_to_e3"
    exit 1
  fi
fi