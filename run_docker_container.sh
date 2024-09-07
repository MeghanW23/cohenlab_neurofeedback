#!/bin/bash 

echo "Setting correct x11 access"
xhost + 

echo "Pulling any repo changes"
git pull origin main 

echo "Running Docker"
# docker run -it --rm -v "$(pwd):/workdir" nfb_docker:1.0 /bin/bash
docker run -it --rm \
    -e DISPLAY=host.docker.internal:0 \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v "$(pwd):/workdir" \
    -v /Users/meghan/sambashare:/workdir/run_docker/sambashare \
    nfb_docker:1.0 \
    /bin/bash


