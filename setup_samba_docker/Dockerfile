# Use a lightweight Linux base image
FROM debian:bullseye-slim

# Update and install Samba
RUN apt-get update && apt-get install -y samba smbclient systemctl sudo nano && apt-get clean

COPY smb.conf /etc/samba

# Expose the default Samba ports
EXPOSE 137 138 139 445

# additional setup done via a running container and then commmiting the container to the image:
# NOTE: if your UID and GID for the host user receiving the data outside of the container is NOT 501 and 20, respectively - you will need to edit the UID and GID in your own image
#   sudo useradd -u "$USER_UID" -g "$USER_GID" smbuser # create smbuser account with valid uid and gid
#   sudp passwd smbuser # add password to smbuser account 
#   sudo chown smbuser:"$USER_GID" /sambashare # smbuser owns sambashare dir
#   sudo smbpasswd -a smbuser # add smbuser via password to samba 
#   sudo smbpasswd -e smbuser # enable smbuser for samba