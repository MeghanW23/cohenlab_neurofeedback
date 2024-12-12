FROM debian:bullseye-slim

# Set the working directory
WORKDIR /workdir

# Copy the smb.conf file from the build context into the container
COPY smb.conf /workdir/smb.conf

# Install Samba
RUN apt-get update && apt-get install -y samba