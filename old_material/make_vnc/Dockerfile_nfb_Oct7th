FROM ubuntu:20.04

# Set the timezone and configure tzdata for non-interactive installation
ENV TZ=America/New_York
ENV DEBIAN_FRONTEND=noninteractive
ENV USER=root

# Combine installation of XFCE, VNC server, and necessary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    xfce4 \
    xfce4-goodies \
    tightvncserver \
    dbus-x11 \
    xfonts-base \
    sudo \
    git \
    python3 \
    python3-venv \
    rsync \
    wget \
    gnupg \
    nano \
    dcm2niix \
    libc6 \
    tzdata && \
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Setup VNC server
RUN mkdir /root/.vnc \
    && echo "bchcohenlab" | vncpasswd -f > /root/.vnc/passwd \
    && chmod 600 /root/.vnc/passwd

# Create an .Xauthority file
RUN touch /root/.Xauthority


# Set display resolution (change as needed)
ENV RESOLUTION=1920x1080

# Expose VNC port
EXPOSE 5901

# Set the working directory
WORKDIR /workdir

# Copy the contents to the working directory
COPY . /workdir

RUN chmod +x start-vnc.sh

# Run the FSL installer with the --skip_registration flag and set the installation directory
# RUN python3 /workdir/fslinstaller.py --skip_registration --dest=/usr/local/fsl

# Set the entry point
ENTRYPOINT ["/bin/bash", "/workdir/startup_docker.sh"]
