#!/bin/bash

python fslinstaller.py

# Append the necessary exports to .bashrc
echo "export FSLDIR=/usr/local/fsl" >> /root/.bashrc
echo "export PATH=\$FSLDIR/bin:\$PATH" >> /root/.bashrc
echo "export USER=$(whoami)" >> /root/.bashrc

# Source the FSL script
echo ". \$FSLDIR/etc/fslconf/fsl.sh" >> /root/.bashrc
