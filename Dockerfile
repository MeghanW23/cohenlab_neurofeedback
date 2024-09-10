# Use Python 3.10.10 Slim image as base
FROM python:3.10.10-bullseye

# Set the working directory in the container
WORKDIR /workdir

# Copy the Repo into the docker image
COPY . /workdir

# Install Git and other necessary packages
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install any required packages
RUN pip install --no-cache-dir -r requirements.txt

# Set startup script as the entry point
ENTRYPOINT ["./startup_docker.sh"]