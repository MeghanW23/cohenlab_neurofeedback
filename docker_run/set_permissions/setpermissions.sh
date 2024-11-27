#!/bin/bash
# Used to set the permissions of new dicoms from the scanner 
# Must be run on the user that is receiving the DICOMS 

if [ "$(whoami)" != "samba_user" ]; then
  echo "This script must be run as samba_user!"
  exit 1
fi


HOME="/Users/samba_user"
if [ ! -d "$HOME" ]; then
    echo "Environment variable "HOME" is not a valid directory (check if it is a set env var)".
    exit 1
fi 

sambashare_dir="${HOME}/sambashare"
if [ ! -d "$sambashare_dir" ]; then
    echo "The sambashare directory set: ${sambashare_dir} is not a valid directory."
else
    echo "Listening to directory: ${sambashare_dir}"
    chmod -R 777 "${sambashare_dir}"
fi 

starting_directory_count=$(ls "$sambashare_dir" | wc -l)
day_timestamp=$(date +"%Y_%m_%d")
time_timestamp=$(date +"%H_%M_%S")
echo "Starting to listen Date:${day_timestamp} and Time:${time_timestamp}, with a starting directory count of: "
echo "${starting_directory_count}"

while true; do
    current_directory_count=$(ls "$sambashare_dir" | wc -l)
    if [ "$starting_directory_count" -eq "$current_directory_count" ]; then 
        day_timestamp=$(date +"%Y_%m_%d")
        time_timestamp=$(date +"%H_%M_%S")
        echo "Waiting (Date:${day_timestamp} and Time:${time_timestamp})..."
        sleep 0.1
    else
        new_dir_path="${sambashare_dir}/$(ls -tr ${sambashare_dir} | tail -n 1)"
        echo "Found new dir: ${new_dir_path}"
        echo "Doing command: chmod 777 <new_dir>"
        chmod -R 777 "$new_dir_path"

        while true; do
            chmod -R 777 "$new_dir_path"
            echo "Ran chmod."
            echo "DICOMs found: $(ls "$new_dir_path" | wc -l)"
            sleep 0.1
        done
        echo "Resetting - Listening for new directory..."
        starting_directory_count="$current_directory_count"
        
    fi
done
