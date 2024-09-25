# Use Ubuntu as the base image
FROM ubuntu:24.10

# Set the working directory in the container
WORKDIR /workdir

# Copy the Repo into the docker image
COPY . /workdir

# Install Git, Python, and necessary packages
RUN apt-get update && \
    apt-get install -y git python3 python3-venv rsync && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the entry point
ENTRYPOINT ["./startup_docker.sh"]
