FROM ubuntu:20.04

# Set the timezone and configure tzdata for non-interactive installation
ENV TZ=America/New_York
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update && \
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get install -y sudo git python3 python3-venv rsync wget gnupg nano dcm2niix libc6 tzdata && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /workdir

# Copy the contents to the working directory
COPY . /workdir

# Run the FSL installer with the --skip_registration flag and set the installation directory
RUN python3 /workdir/fslinstaller.py --skip_registration --dest=/usr/local/fsl

# Set the entry point
ENTRYPOINT ["/bin/bash", "/workdir/startup_docker.sh"]
