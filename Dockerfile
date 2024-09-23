# Use Python 3.10.10 Slim image as base
FROM python:3.10-buster

# Set the working directory in the container
WORKDIR /workdir

# Copy the Repo into the docker image
COPY . /workdir

# Install Git and other necessary packages
RUN apt-get update && \
    apt-get install -y \
    git \
    rsync \
    x11-apps \
    xauth \
    libx11-dev \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libglu1-mesa \
    libglx-mesa0 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    mesa-utils \
    python3-tk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install any required packages
RUN pip install --no-cache-dir -r requirements.txt

# Set startup script as the entry point
ENTRYPOINT ["./startup_docker.sh"]