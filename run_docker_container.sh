#!/bin/bash

cd ~/cohenlab_neurofeedback/ || exit

echo "Setting correct x11 access ..."
xhost +

while true; do
  read -p "Pull any repo changes? (y/n): " pull_yn
  if [ "$pull_yn" = "y" ]; then
      echo "Ok, Pulling Repo Changes ... "
      git pull origin main
      break
  elif [ "$pull_yn" = "n" ]; then
      echo "Ok, Not Pulling Repo Changes."
      break
  else
      echo "Please enter either 'y' or 'n'"
  fi
done

echo "Running Docker..."
# docker run -it --rm -v "$(pwd):/workdir" nfb_docker:1.0 /bin/bash
docker run -it --rm \
    -e DISPLAY=host.docker.internal:0 \
    -e USERNAME="$(whoami)" \
    -e TZ=America/New_York \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v "$(pwd):/workdir" \
    -v "$(pwd)/tasks_run/data/sambashare:/workdir/tasks_run/data/sambashare" \
    nfb_docker:1.0 \
    /bin/bash

