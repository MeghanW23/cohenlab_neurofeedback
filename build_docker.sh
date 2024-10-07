#!/bin/bash

set -e  # Exit the script if any command fails

cd ~/cohenlab_neurofeedback/
settings_dirpath="./tasks_run/scripts/"

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
sudo docker build --platform linux/arm64 --no-cache -t nfb_docker:1.0 .

# Make the Docker runner executable
echo "Making Docker Runner Executable..."
for file in "$(pwd)"/run_docker_container*; do
    sudo chmod +x "$file"
done

# Make other necessary scripts executable
echo "Making Alias Script Executable ..."
sudo chmod +x "$(pwd)"/aliases_and_functions.sh && echo "Successful."|| echo "Error making scripts executable. You will need to do this manually."

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
