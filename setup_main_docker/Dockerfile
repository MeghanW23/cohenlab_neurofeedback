FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/New_York

# Install dependencies and clean up
RUN apt-get update && \
    apt-get install -y psmisc sudo git python3 python3-venv rsync wget gnupg nano dcm2niix libc6 python3-pip x11-xserver-utils xorg x11vnc xvfb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /workdir

COPY ./python_requirements.txt /workdir/python_requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r /workdir/python_requirements.txt
