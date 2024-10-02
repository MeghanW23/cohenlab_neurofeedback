#!/bin/bash

set -e  # Exit the script if any command fails

REPO_URL="https://github.com/MeghanW23/cohenlab_neurofeedback"
username="$(whoami)"
user_file="./users.txt"

echo "Building ADHD Stimulant, Motion, and Neurofeedback Project Docker Image"

# Pull new changes from the repository
while true; do
  read -p "Pulling any new changes to the repo first? (y/n): " choice
  case "$choice" in
    y|Y )
      echo "Ok, pulling now ..."
      git fetch
      git pull origin main
      break
      ;;
    n|N )
      echo "Ok, will not pull new changes."
      break
      ;;
    * )
      echo "Please choose either y or n."
      ;;
  esac
done

# Build the Docker image
echo "Building Docker image..."
sudo docker build --platform linux/amd64 --no-cache -t nfb_docker:1.0 .

# Make the Docker runner executable
echo "Making Docker Runner Executable..."
for file in "$(pwd)"/run_docker_container*; do
    sudo chmod +x "$file"
done

# Make other necessary scripts executable
echo "Making all other necessary scripts executable..."
scripts=("startup_docker.sh" "aliases_and_functions.sh" "get_ssh_keys.sh" "make_venv.sh" "tasks_run/scripts/RegisterFnirt.sh" "tasks_run/scripts/TransferFilesE3.sh" "tasks_run/scripts/PreprocRegisterE3.sh")

for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        sudo chmod +x "$script"
    else
        echo "Warning: $script not found."
    fi
done

# Add the user's username to the record if not already added
echo "Adding your username to Docker records, if not already added..."
if ! grep -q "$username" "$user_file"; then
  while true; do
    read -p "Please enter your CH ID: " chid
    if [[ "$chid" != ch* ]]; then
      echo "Please ensure your CH ID includes 'ch'."
    else
      echo "Ok, using CH ID: ${chid}."
      echo "${username}, ${chid}" >> "$user_file"
      echo "Your user information is added to ${user_file}:"
      grep "$username" "$user_file"
      break
    fi
  done
else
  echo "Your user information is already added:"
  grep "$username" "$user_file"
fi

echo -e "Hello, ${username}. Docker image creation is complete."

# Prompt to start additional setup
while true; do
  read -p "Additional software and setup will need to be built into the image. This process may take up to 2 hours. Start now? (y/n): " setup_container
  case "$setup_container" in
    y|Y )
      echo "Ok, starting now..."
      ./run_docker_container.sh
      break
      ;;
    n|N )
      echo "Ok, you can finish setup at any time by running: ./run_docker_container.sh"
      break
      ;;
    * )
      echo "Please enter either 'y' or 'n'."
      ;;
  esac
done
