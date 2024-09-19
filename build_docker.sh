#!/bin/bash

# Define the repository URL
REPO_URL="https://github.com/MeghanW23/cohenlab_neurofeedback"

echo "Pulling Any New Changes to the Repo..."
git pull origin main

# Build the Docker image
echo "Building Docker image..."
sudo docker build -t nfb_docker:1.0 .

echo "Making Docker Runner Executable..."

for file in $(pwd)/run_docker_container*
do 
    sudo chmod +x "$file"
done 

echo "Making All Other Necessary Scripts Executable ..."
sudo chmod +x startup_docker.sh
sudo chmod +x ssh_e3.sh


echo "All Set!"
echo "Run run_docker_container.sh to run the docker image"
