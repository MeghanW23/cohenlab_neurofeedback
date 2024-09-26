#!/bin/bash

wget -O- http://neuro.debian.net/lists/focal.us-nh.full | sudo tee /etc/apt/sources.list.d/neurodebian.sources.list
sudo apt-key adv --recv-keys --keyserver hkps://keyserver.ubuntu.com 0xA5D32F012649A5A9
sudo apt-get update
sudo apt-get install -y fsl

# Append the necessary exports to .bashrc
echo "export FSLDIR=/usr/share/fsl/5.0" >> /root/.bashrc
echo "export PATH=\$FSLDIR/bin:\$PATH" >> /root/.bashrc
echo "export USER=$(whoami)" >> /root/.bashrc

# Source the FSL script
echo ". \$FSLDIR/etc/fslconf/fsl.sh" >> /root/.bashrc
