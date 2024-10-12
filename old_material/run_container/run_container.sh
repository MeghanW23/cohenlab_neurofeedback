#!/bin/bash
arch=""
while true; do
  read -p "Run with AMD64 or or ARM64 architecture? (amd/arm): " arch
  if [ "$arch" = "amd" ]; then
    echo "Ok, running with amd architecture ..."
    break
  elif [ "$arch" = "arm" ]; then
    echo "Ok, running with arm architecture ..."
    break
  else
    echo "Please type either 'amd' or 'arm'"
  fi
done

if  [ "$arch" = "amd" ]; then
  docker run -it --rm \
    --platform linux/amd64 \
    -e DISPLAY=host.docker.internal:0 \
    -e USERNAME="$(whoami)" \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v /Users/meghan/multiarch_docker/:/workdir/ \
    meghanwalsh/multiarch_nfb_docker:latest-amd64 \
    /bin/bash
else
    docker run -it --rm \
      --platform linux/arm64 \
      -e DISPLAY=host.docker.internal:0 \
      -e USERNAME="$(whoami)" \
      -v /tmp/.X11-unix:/tmp/.X11-unix \
      -v /Users/meghan/multiarch_docker/:/workdir/ \
      meghanwalsh/multiarch_nfb_docker:latest-arm64 \
      /bin/bash

fi