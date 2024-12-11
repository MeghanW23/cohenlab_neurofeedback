# Setup and Information for Creating the Samba File Server on Docker Image
Meghan Walsh 

## Steps to Create the Docker Image 
### 1. Create the `smb.conf` file 
[Link to Current `smb.conf` File](https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/setup_samba_docker/smb.conf)

##### Global Section:
`[global]:` This section defines global settings that apply to the whole Samba service.

`workgroup = WORKGROUP`: Defines the workgroup name that Samba will be a part of. WORKGROUP is the default for Windows-based networks, and all Samba clients must be part of the same workgroup to communicate.

`server string = Samba Server`: This is a description string that identifies the server on the network. It's displayed when browsing the network.

`netbios name = SAMBASERVER`: Specifies the NetBIOS name of the server. This is how the server will be identified over the network (in this case, "SAMBASERVER"). NetBIOS is used for older Windows networking protocols.

`security = user`: Defines the security model. In this case, it's set to "user", which means Samba will require users to authenticate with a username and password.

`map to guest = bad user`: This directive tells Samba to map any failed login attempts (due to incorrect credentials) to the "guest" user account. This is often used to allow guests access if they don't have proper authentication credentials.

#### Samba Share Section:
`[sambashare]`: This defines a specific share (in this case, a folder named "sambashare") that will be accessible over the network.

`path = /sambashare`: Specifies the directory on the server that will be shared. In this case, it's the directory /sambashare on the server. This directory is mapped from a location on the host machine

`browsable = yes`: Allows the shared directory to be visible when browsing the network. If set to "no", users would need to know the exact path to access the share.

`writable = yes`: Allows users to write (modify or add files) in the shared directory. If set to "no", the share would be read-only for all users.

`guest ok = yes`: Allows guest access to the shared directory, meaning users can access the share without a username or password.

`read only = no:` This is another way to specify whether the share is read-only or writable. "no" means the share is writable.

`create mask = 0777`: Sets the file permissions for newly created files in the share. The 0777 permission gives read, write, and execute access to the owner, group, and others.

`directory mask = 0777`: Sets the directory permissions for newly created directories in the share. Like the create mask, this ensures full access for all users (read, write, execute).

### 2. Create the Dockerfile 
[Link to Current `Dockerfile`](https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/setup_samba_docker/Dockerfile)

This Dockerfile outlines the steps to create a Docker image that sets up a Samba server on a minimal Debian-based container. 
It sets up a container with a Samba server, configured by a custom smb.conf file, and exposes the necessary ports for SMB file sharing. Here's an explanation of each line:

1. `FROM debian:bullseye-slim`: This line specifies the base image for the Docker container. The debian:bullseye-slim image is a minimal version of Debian (specifically the Bullseye release). It's "slim" to keep the image smaller, only including essential components.

2. `RUN apt-get update && apt-get install -y samba systemctl sudo nano && apt-get clean`:
    1. `apt-get update`: Updates the package lists for the Debian package manager.
    2. `apt-get install -y samba systemctl sudo nano`: Installs the Samba package, systemctl (for managing system services), sudo (to grant administrative privileges), and nano (a simple text editor).
    3. `apt-get clean`: Cleans up the package cache after installation to reduce the size of the image.

3. `COPY smb.conf /etc/samba`: This line copies a local smb.conf file (presumably containing the Samba configuration) from the host machine into the container's /etc/samba directory. This configures Samba within the container.

4. `EXPOSE 137 138 139 445`: This line exposes the ports used by Samba for communication. These ports need to be exposed to allow Samba to communicate with clients on the network. The ports exposed are: 
    1. `137`: NetBIOS Name Service (used for name resolution).
    2. `138`: NetBIOS Datagram Service (used for sending messages).
    3. `139`: NetBIOS Session Service (used for file sharing).
    4. `445`: Microsoft-DS (used for SMB/CIFS file sharing)

### 3. Build the Dockerfile 
To build, navigate to the directory in which your `smb.conf` and `Dockerfile` are located and run: 
```
sudo docker build -t nfb_samba_share .
```

### 4. Push to DockerHub
If you want to push your image to DockeHub, do the following steps: 
1. Tag your image:

    ```
    docker tag nfb_samba_share meghanwalsh/nfb_samba_share:latest
    ```
2. Push your image to your DockerHub account: 
    ```
    docker push meghanwalsh/nfb_samba_share:1.0
    ```

