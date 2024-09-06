#!/bin/bash

# set up any aliases needed during the container runtime
echo "alias rifg='python /workdir/run_docker/rifg_task/rifg_task.py'" >> ~/.bashrc
source ~/.bashrc
exec "$@"

