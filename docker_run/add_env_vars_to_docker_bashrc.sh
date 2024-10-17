#!/bin/bash

# Script used to take the config variables in the config.env file
# and put them in the docker container's .bashrc so they can be used by scripts to be run in the container.

# Get the parent directory of the script
parent_dir=$(dirname "$(realpath "$0")")
config_path="${parent_dir}/config.env"

# Check if the config file exists
if [[ ! -f "$config_path" ]]; then
    echo "Error: Config file '$config_path' does not exist."
    exit 1
fi

# Read the config file and add variables to .bashrc
while read -r line; do
    if [[ -n "$line" && "$line" != \#* ]]; then
        # Only add the variable if it's not already present in .bashrc
        if ! grep -qF "$line" ~/.bashrc; then
            echo "export $line" >> ~/.bashrc
        fi
    fi
done < "$config_path"  # Changed from $ENV_FILE to $config_path

# Reload .bashrc to apply the changes immediately
source ~/.bashrc

echo "Environment variables from $config_path have been added to ~/.bashrc and applied."
