#!/bin/bash

# Define the repository URL
REPO_URL="https://github.com/MeghanW23/cohenlab_neurofeedback"

# Clone the repository if it doesn't exist
if [ ! -d "./cohenlab_neurofeedback" ]; then
  echo "Repository not found. Cloning..."
  git clone "$REPO_URL" ./cohenlab_neurofeedback
else
  echo "Repository found. Pulling latest changes..."
  # Go to the repo directory and pull the latest changes
  cd ./cohenlab_neurofeedback
  git pull origin main
  cd ..
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t nfb_docker:1.0 .
