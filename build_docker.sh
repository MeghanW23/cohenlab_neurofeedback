#!/bin/bash

# Define the repository URL
REPO_URL="https://github.com/MeghanW23/cohenlab_neurofeedback"

echo "Pulling Any New Changes to the Repo..."
git pull origin main

# Build the Docker image
echo "Building Docker image..."
sudo docker build -t nfb_docker:1.0 .
