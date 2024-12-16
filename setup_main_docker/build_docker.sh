#!/bin/bash

echo "To build a multiarch docker image, we will need to push the created image to your dockerhub account."
read -p "Enter your dockerfile username: " docker_username
echo "This project's docker image uses the name 'nfb_docker'. If this is not true for you, please swap out all mentions of 'nfb_docker' in the project to your project name."
read -p "Name the image: " docker_image

echo "Tips for docker building: "
echo "  1. If you are using a VPN, it is recommended you disconnect."
echo "      (VPNs can cause intermittent network issues which may cause network interruptions when pushing the image to your dockerhub account.)" 
echo "  2. Running this script with 'sudo' may be necessary."
read -p "Press enter to continue. "

# Create docker builder
if ! docker buildx inspect multi-arch > /dev/null 2>&1; then
    echo "Docker builder 'multiarch_docker' does not exist. Creating it..."
    sudo docker buildx create --driver-opt network=host --use --name multiarch_docker
else
    echo "Docker builder 'multiarch_docker' already exists. Using it..."
    docker buildx use multiarch_docker
fi

# Build docker image
# echo "Building Docker image and pushing two tags (1.0 and latest) to dockerhub..."
# docker buildx build --platform linux/amd64,linux/arm64 -t "$docker_username"/${docker_image}:1.0 --push .

docker buildx build --platform linux/amd64,linux/arm64 -t meghanwalsh/${docker_image}:latest --push .

echo "Removing builder now ..."
docker buildx rm multiarch_docker
