FROM openjdk:11-jdk-slim

WORKDIR /workdir

RUN apt-get update && apt-get install -y \
    sudo nano python3 maven x11vnc xvfb \
    libgtk-3-0 libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*

