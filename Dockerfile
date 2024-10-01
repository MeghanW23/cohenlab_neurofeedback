FROM ubuntu:20.04

# Set the timezone to your desired zone, e.g., 'America/New_York'
ENV TZ=America/New_York

RUN apt-get update && \
    apt-get install -y sudo git python3 python3-venv rsync wget gnupg nano dcm2niix libc6 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /workdir

# Copy the contents to the working directory
COPY . /workdir

# Make the install script executable
# RUN chmod +x /workdir/install_fsl.sh

# Run the install script
# RUN /workdir/install_fsl.sh

# Set the entry point
ENTRYPOINT ["bash", "./startup_docker.sh"]