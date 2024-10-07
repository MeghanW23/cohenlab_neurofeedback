FROM ubuntu:22.04

# Install necessary packages
RUN apt-get update && apt-get install -y \
    xfce4 \
    xfce4-goodies \
    x11vnc \
    xvfb \
    supervisor \
    && apt-get clean

# Set a password for VNC access
RUN mkdir -p /root/.vnc && \
    x11vnc -storepasswd 1234 /root/.vnc/passwd

# Set up the VNC server to start with Xfce4
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose VNC port
EXPOSE 5900

# Start the VNC server
CMD ["/usr/bin/supervisord"]

