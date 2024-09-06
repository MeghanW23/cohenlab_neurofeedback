#!/bin/bash

# Define the repository URL
REPO_URL="https://github.com/MeghanW23/cohenlab_neurofeedback"

echo "Pulling Any New Changes to the Repo..."
git pull origin main

# Build the Docker image
echo "Building Docker image..."
sudo docker build -t nfb_docker:1.0 .

echo "Making Docker Runner Executable..."
sudo chmod +x run_docker_container.sh

echo "Making Docker Startup Script Executable ..." 
sudo chmod +x startup_docker.sh

echo "All Set!"
echo "Run run_docker_container.sh to run the docker image"
