#!/bin/bash

wget -O- http://neuro.debian.net/lists/jammy.us-ca.libre | tee /etc/apt/sources.list.d/neurodebian.sources.list
apt-key adv --recv-keys --keyserver hkps://keyserver.ubuntu.com 0xA5D32F012649A5A9
sudo apt-get update
sudo apt-get install fsl