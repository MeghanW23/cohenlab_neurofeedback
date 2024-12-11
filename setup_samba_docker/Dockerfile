# Use a lightweight Linux base image
FROM debian:bullseye-slim

# Update and install Samba
RUN apt-get update && apt-get install -y samba systemctl sudo nano && apt-get clean

COPY smb.conf /etc/samba

# Expose the default Samba ports
EXPOSE 137 138 139 445
