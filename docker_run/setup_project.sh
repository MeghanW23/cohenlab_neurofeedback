#!/bin/bash

function find_path_env_variable {
  local basename=$1            # The name of the file
  local local_varname=$2       # The local environment variable name
  local docker_varname=$3      # The docker environment variable name
  local in_local_dir=$4        # The local directory where the file is located
  local in_docker_dir=$5       # The docker directory where the file is located
  local local_config_file=$6   # The local configuration file where the variable is stored
  local docker_config_file=$7  # The docker configuration file where the variable is stored

  if [ -z "$basename" ]; then
    echo "Empty filename for variable: ${local_varname} and/or ${docker_varname})"
    exit 1
  fi

  # Construct the full path
  local local_full_path="${in_local_dir}/${basename}"
  local docker_full_path="${in_docker_dir}/${basename}"

  # Check if the variable is already in the config file
  if ! grep -q "^${local_varname}=" "$local_config_file"; then
    echo "Adding env variable ${local_varname} as ${local_full_path} ..."
    echo "${local_varname}=\"${local_full_path}\"" >> "$local_config_file" || {
      echo "Failed to write to ${local_config_file}"
      exit 1
    }
  else
    echo "Variable ${local_varname} already exists in ${local_config_file}."
  fi

    # Check if the variable is already in the config file
  if ! grep -q "^${docker_varname}=" "$local_config_file"; then
    echo "Adding env variable ${docker_varname} as ${docker_varname} ..."
    echo "${docker_varname}=\"${docker_full_path}\"" >> "$local_config_file" || {
      echo "Failed to write to ${docker_config_file}"
      exit 1
    }
  else
    echo "Variable ${docker_varname} already exists in ${local_config_file}."
  fi

}

function user_get_env_variable {
    local env_var_name=$1          # The name of the environment variable
    local docker_var_name=$2       # The name of the environment variable
    local path=$3                  # 0 if the variable is a path, 1 if it's just a string
    local docker_dir_path=$4       # For the paths that require a docker path as well
    local env_file=$5              # The configuration file to store the environment variable
    local message_to_user=$6       # Message prompting the user for the variable's value

    echo "Checking for variable $env_var_name in $env_file .."
    if ! grep -q "^${env_var_name}=" "$env_file"; then
      echo "$env_var_name not found in $env_file. Please set it now."
      echo "$message_to_user"
      while true; do
        read -p "Set value for $env_var_name: " VARIABLE
        if [ "$path" = 0 ]; then
          # Check if the provided variable is a valid path
          if [ -e "$VARIABLE" ]; then
            echo "$env_var_name=\"$VARIABLE\"" >> "$env_file" || {
              echo "Failed to write to ${env_file}"
              exit 1
            }
            echo "$env_var_name is now set to $VARIABLE in config file."
            echo "$docker_var_name=\"${docker_dir_path}/$(basename "$VARIABLE")\"" >> "$env_file" || {
              echo "Failed to write to ${env_file}"
              exit 1
            }
            echo "$docker_var_name is now set to \"${docker_dir_path}/$(basename "$VARIABLE")\" in config file."
            break
          else
            echo "Could not find the inputted path on your local machine. Try again."
          fi
        else
          # Store the variable directly as a string
          echo "$env_var_name=$VARIABLE" >> "$env_file" || {
            echo "Failed to write to ${env_file}"
            exit 1
          }
          echo "$env_var_name is now set to $VARIABLE in config file."
          break
        fi
      done
    else
      echo "Found $env_var_name in $env_file"
    fi
}

echo -e "\nSetup script for project: Impact of Stimulants and In-Scanner Motion on fMRI Neurofeedback and Task Performance in ADHD.\n"

# --------------------------------------------------
# ---------- Set startup variables here ------------

local_dir_path=$(dirname "$(realpath "$0")")

docker_dir_path="/workdir/docker_run"

LOCAL_CONFIG_FILE="$local_dir_path/config.env"

DOCKER_CONFIG_FILE="$docker_dir_path/config.env"

DISPLAY="host.docker.internal:0"

# ---------- Set startup variables here ------------
# --------------------------------------------------

# Add user information header if not present
if ! grep -q "# User information" "$LOCAL_CONFIG_FILE"; then
  echo -e "\n# User information" >> "$LOCAL_CONFIG_FILE"
fi
# Add the username to the config file
if ! grep -q "USER=" "$LOCAL_CONFIG_FILE"; then
  echo "Adding your project username via 'whoami' command ..."
  echo "USER=$(whoami)" >> "$LOCAL_CONFIG_FILE"
fi

user_get_env_variable "CHID" "None" 1 "None" "$LOCAL_CONFIG_FILE" "Set your BCH ID in order to send and receive files from e3"

# Set base paths
echo "Recording base paths and setting path environment variables ..."
if ! grep -q "# Base Paths" "$LOCAL_CONFIG_FILE"; then
  echo -e "\n# Base Paths" >> "$LOCAL_CONFIG_FILE"
fi

find_path_env_variable "config.env" "LOCAL_CONFIG_FILE_PATH" "DOCKER_CONFIG_FILE_PATH" "$local_dir_path" "$docker_dir_path" "$LOCAL_CONFIG_FILE" "$DOCKER_CONFIG_FILE"
find_path_env_variable "docker_run" "LOCAL_RUN_DOCKER_DIR_PATH" "DOCKER_RUN_DOCKER_DIR_PATH" "$(dirname "$local_dir_path")" "$(dirname "$docker_dir_path")" "$LOCAL_CONFIG_FILE" "$DOCKER_CONFIG_FILE"
find_path_env_variable "startup.sh" "LOCAL_SETUP_CONTAINER_FILE_PATH" "DOCKER_SETUP_CONTAINER_FILE_PATH" "$local_dir_path" "$docker_dir_path" "$LOCAL_CONFIG_FILE" "$DOCKER_CONFIG_FILE"
user_get_env_variable "LOCAL_DATA_AND_TASK_PATH" "DOCKER_DATA_AND_TASK_PATH" 0 "/workdir" "$LOCAL_CONFIG_FILE" "Set your project path using DATA_AND_TASK_PATH. This path will pull the scripts necessary to input/output data to the container."

# Print the config file content for verification
echo -e "Contents of ${LOCAL_CONFIG_FILE}:"
cat "$LOCAL_CONFIG_FILE"
echo -e "You may manually edit these paths at any time.\n"

# Sourcing the config file
echo "Sourcing $LOCAL_CONFIG_FILE ..."
if [ -f "$LOCAL_CONFIG_FILE" ]; then
    # Source the entire config file
    source "$LOCAL_CONFIG_FILE"

    echo -e "Sourced $LOCAL_CONFIG_FILE successfully.\n"
else
    echo -e "Failed to source $LOCAL_CONFIG_FILE. File does not exist.\n" >&2
    exit 1
fi

echo "Making the scripts executable ..."
executables=("$LOCAL_RUN_DOCKER_DIR_PATH" "$LOCAL_SETUP_CONTAINER_FILE_PATH")
for script in "${executables[@]}"; do
  sudo chmod +x "$script" || {
    echo "Failed to make ${script} executable."
    exit 1
  }
  echo "Script: ${script} is executable"
done
echo -e "All necessary scripts are executable.\n"

echo "Pulling nfb image now ..."

# Add other necessary info
if ! grep -q "# Other Variables" "$LOCAL_CONFIG_FILE"; then
  echo -e "\n# Other Variables" >> "$LOCAL_CONFIG_FILE"
fi

if ! grep -q "DISPLAY" "$LOCAL_CONFIG_FILE"; then
  echo "DISPLAY=${DISPLAY}" >> "$LOCAL_CONFIG_FILE"
fi

# Add other necessary info
if ! grep -q "# Input Paths to task scripts here" "$LOCAL_CONFIG_FILE"; then
  echo -e "\n# Input Paths to task scripts here" >> "$LOCAL_CONFIG_FILE"
fi
# Uncomment the following line to pull the Docker image
docker pull meghanwalsh/nfb_docker:latest
