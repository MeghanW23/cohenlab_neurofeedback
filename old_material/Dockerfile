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

# Conditionally install FSL only for the amd64 architecture
RUN if [ "$(uname -m)" = "x86_64" ]; then \
        echo "Running FSL installer on amd64"; \
        python3 /workdir/fslinstaller.py --skip_registration --dest=/usr/local/fsl; \
    else \
        echo "Skipping FSL installation on non-amd64 architecture"; \
    fi

# Set the entry point
ENTRYPOINT ["/bin/bash", "/workdir/startup_docker.sh"]
