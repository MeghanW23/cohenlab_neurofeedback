#!/bin/bash

echo "To build a multiarch docker image, we will need to push the created image to your dockerhub account."
read -p "Enter your dockerfile username: " docker_username

# Create docker builder
if ! docker buildx inspect multi-arch > /dev/null 2>&1; then
    echo "Docker builder 'multiarch_docker' does not exist. Creating it..."
    sudo docker buildx create --driver-opt network=host --use --name multiarch_docker
else
    echo "Docker builder 'multiarch_docker' already exists. Using it..."
    docker buildx use multiarch_docker
fi

# Build docker image
echo "Building Docker image and pushing two tags (1.0 and latest) to dockerhub..."
docker buildx build --platform linux/amd64,linux/arm64 -t "$docker_username"/nfb_docker:1.0 --push .

docker buildx build --platform linux/amd64,linux/arm64 -t meghanwalsh/nfb_docker:latest --push .

echo "Removing builder now ..."
docker buildx rm multiarch_docker
