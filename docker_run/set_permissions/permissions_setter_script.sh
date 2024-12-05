#!/bin/bash 

# Assure paths are correct 
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
    # chmod -R 777 "${sambashare_dir}" # First permissions change is run immediately on the whole sambashare_dir
fi 

if [ -z "$WAIT_OR_START" ]; then 
    echo "Needed env variable: WAIT_OR_START is empty."
    echo "Please assure you are not running this script directly. Run the script that runs this script w/ nohup."
    exit 1
elif [ "$WAIT_OR_START" = "start" ]; then 
    echo "Starting now..." 
    
    most_recent_dirpath="${sambashare_dir}/$(ls -tr ${sambashare_dir} | tail -n 1)"
    echo "Permission-setting on directory: ${most_recent_dirpath}"
    if [ -z "$USER" ]; then 
        echo "Skipping dicom-dir ownership check because env var: USER is empty."
    else
        echo "Original User: ${USER}"
        owner=$(stat -f '%Su' "$most_recent_dirpath")
        group=$(stat -f '%Sg' "$most_recent_dirpath")
        echo "DICOM Directory is owned by: ${owner} and in group: ${group}"
        if [ "$owner" = "$USER" ]; then 
            echo "You cannot use the permission-setter on directories and files owned by your personal user (${USER})"
            exit 1 
        fi 
    fi
    echo "Doing command: chmod 777 <new_dir>"
    chmod -R 777 "$most_recent_dirpath"
    while true; do
        chmod -R 777 "$most_recent_dirpath"
        echo "Ran chmod."
        echo "DICOMs found: $(ls "$most_recent_dirpath" | wc -l)"
        sleep 0.1
    done
elif [ "$WAIT_OR_START" = "wait" ]; then 
    echo "Waiting for new directory..."

    # Get starting information
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
        if [ -z "$USER" ]; then 
            echo "Skipping dicom-dir ownership check because env var: USER is empty."
        else
            echo "Original User: ${USER}"
            owner=$(stat -f '%Su' "$new_dir_path")
            group=$(stat -f '%Sg' "$new_dir_path")
            echo "DICOM Directory is owned by: ${owner} and in group: ${group}"
            if [ "$owner" = "$USER" ]; then 
                echo "You cannot use the permission-setter on directories and files owned by your personal user (${USER})"
                exit 1 
            fi 
        fi

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
else
    echo "WAIT_OR_START must equal either 'wait' or 'start'"
fi 

