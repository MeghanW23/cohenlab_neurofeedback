FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/New_York

RUN apt-get update && \
    apt-get install -y sudo git python3 python3-venv rsync wget gnupg nano dcm2niix libc6 python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /workdir
COPY . /workdir/docker-setup/

RUN pip3 install --no-cache-dir -r /workdir/docker-setup/python_requirements.txt
