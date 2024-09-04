#!/bin/bash 

echo "Pulling any repo changes"
git pull origin main 

echo "Running Docker"
docker run -it --rm -v "$(pwd):/workdir" nfb_docker:1.0 /bin/bash
# docker run -it nfb_docker:1.0 /bin/bash
