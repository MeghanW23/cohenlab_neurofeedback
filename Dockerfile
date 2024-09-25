# Use Ubuntu as the base image
FROM ubuntu:20.04

# Set the working directory in the container
WORKDIR /workdir

# Copy the Repo into the docker image
COPY . /workdir

# Install Git, Python, and necessary packages
RUN apt-get update && \
    apt-get install -y sudo git python3 python3-venv rsync wget gnupg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN chmod +x /workdir/install_fsl.sh
RUN /workdir/install_fsl.sh

# Set the entry point
ENTRYPOINT ["./startup_docker.sh"]
