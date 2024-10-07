# Stage 1: Install FSL on x86_64 using emulation
FROM --platform=linux/amd64 ubuntu:20.04 AS fsl

# Set the timezone and configure tzdata for non-interactive installation
ENV TZ=America/New_York
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages for FSL
RUN apt-get update && \
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get install -y sudo git python3 wget libc6 tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /workdir

# Copy the FSL installer script
COPY fslinstaller.py /workdir/

# Run the FSL installer with the --skip_registration flag and set the installation directory
RUN python3 fslinstaller.py --skip_registration --dest=/usr/local/fsl

# Stage 2: Set up arm64 environment
FROM --platform=linux/arm64 ubuntu:20.04 AS arm64

# Set the timezone and configure tzdata for non-interactive installation
ENV TZ=America/New_York
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages for arm64 programs
RUN apt-get update && \
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get install -y sudo git python3 python3-venv rsync wget gnupg nano dcm2niix libc6 tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy FSL from the x86_64 build
COPY --from=fsl /usr/local/fsl /usr/local/fsl

# Set the working directory for ARM64
WORKDIR /workdir

# Copy the contents to the working directory (for ARM64)
COPY . /workdir

# Set the entry point
ENTRYPOINT ["/bin/bash", "/workdir/startup_docker.sh"]
