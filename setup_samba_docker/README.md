# Steps to Making the Sambashare Docker Container 
*Meghan Walsh*


## 1. Create the smb.conf File
[smb.conf file](https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/setup_samba_docker/smb.conf)
- `workgroup = WORKGROUP`: Specifies the workgroup or domain that the Samba server will belong to when interacting with other computers in a network.
- ` server string = Samba Server`: The server string in a Samba configuration file (smb.conf) is a descriptive name for the Samba server. This string does not affect the functionality of the Samba service but is used to provide a human-readable description of the server in network environments where it is listed.
- `security = user`: The server uses user-level authentication, which requires clients to provide a valid username and password to access shared resources.
- `browsable = yes`: Means the share will be listed when users browse the network from a file manager (like Windows File Explorer).
- `read only = no`: This allows users to add or modify files in the shared directory.
- `guest ok = yes`: allows guest access, meaning users can access the share without providing a username or password.


## 2. Make Dockerfile 
![Dockerfile](https://raw.githubusercontent.com/MeghanW23/cohenlab_neurofeedback/refs/heads/main/setup_samba_docker/Dockerfile)
- form a lightweight, linux image
- install samba into image 

run this comment to build the docker image: 
```
cd <path_to_cohenlab_neurofeedback>/setup_samba_docker && sudo docker build -t samba_nfb_docker:1.0 .
```
