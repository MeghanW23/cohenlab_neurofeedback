#!/bin/bash

# set up any aliases needed during the container runtime
echo "alias rifg='python /workdir/run_docker/rifg_task/rifg_task.py'" >> ~/.bashrc
echo "alias calculate='python /workdir/tasks_run/scripts/main.py'" >> ~/.bashrc
echo "alias data='cd /workdir/tasks_run/data/'" >> ~/.bashrc
echo "alias logs='cd /workdir/tasks_run/data/logs'" >> ~/.bashrc
echo "alias scripts='cd /workdir/tasks_run/data/scripts'" >> ~/.bashrc

source ~/.bashrc
exec "$@"

