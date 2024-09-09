# Use Python 3.10.10 Slim image as base
FROM python:3.10.10-slim-bullseye

# Set the working directory in the container
WORKDIR /workdir

# Copy the Repo into the docker image
COPY . /workdir

# Install Git and other necessary packages
RUN apt-get update && \
    apt-get install -y git libc6 libstdc++6 wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download and install dcm2niix
RUN wget https://github.com/rordenlab/dcm2niix/releases/download/v1.0.20230411/dcm2niix_lnx.zip && \
    unzip dcm2niix_lnx.zip -d /usr/local/bin/ && \
    rm dcm2niix_lnx.zip

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install any required packages
RUN pip install --no-cache-dir -r requirements.txt

# Set startup script as the entry point
ENTRYPOINT ["./startup_docker.sh"]