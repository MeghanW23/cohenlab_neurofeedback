#!/bin/bash

# Add any aliases here
echo "alias home='cd /workdir/'" >> ~/.bashrc
echo "alias venv='source /workdir/venv/bin/activate'" >> ~/.bashrc
if [ -z "$CHID" ]; then
  echo "----------"
  echo "WARNING: CHID is empty"
  echo "----------"
fi
echo "alias e3='ssh -F /workdir/.ssh/config_${CHID} e3_${CHID}'" >> ~/.bashrc

source ~/.bashrc