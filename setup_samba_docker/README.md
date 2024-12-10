# Steps to Making the Sambashare Docker Container 
Meghan Walsh


## 1. Create the smb.conf File
[smb.conf](https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/setup_samba_docker/smb.conf)
- `workgroup = WORKGROUP`: Specifies the workgroup or domain that the Samba server will belong to when interacting with other computers in a network.
- ` server string = Samba Server`: The server string in a Samba configuration file (smb.conf) is a descriptive name for the Samba server. This string does not affect the functionality of the Samba service but is used to provide a human-readable description of the server in network environments where it is listed.
- `security = user`: The server uses user-level authentication, which requires clients to provide a valid username and password to access shared resources.
- `browsable = yes`: Means the share will be listed when users browse the network from a file manager (like Windows File Explorer).
- `read only = no`: This allows users to add or modify files in the shared directory.
- `guest ok = yes`: allows guest access, meaning users can access the share without providing a username or password.


## 2. Make Dockerfile 
[Dockerfile](https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/setup_samba_docker/Dockerfile)
- form a lightweight, linux image
- install samba into image 

run this comment to build the docker image: 
```
cd <path_to_cohenlab_neurofeedback>/setup_samba_docker && sudo docker build -t samba_nfb_docker:1.0 .
```

## 3. Start Sambashare Service in Running Docker Container 
Run a container with ports exposed:
```
docker run -d \
    --name samba \
    -p 139:139 \
    -p 1445:445 \
    -v /Users/samba_user/sambashare:/sambashare \
    samba_nfb_docker:1.0 -p
```

If the port on your machine is already allocated, try a different port. (For example, on my machine, `launchd` is already listening on port 445 so I used port 1445)

In the Docker container, start the Samba service:
```
service smbd start
```
Or start in the background 
```
smbd -F
```

## 4. Connect from Remote Client
You will need to enter the following to connect:
1. The docker container's IP 
2. The name of the exported sambashare directory 
3. A valid username and password

![MRI control computer sambashare configuration](https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/setup_samba_docker/MRI_Computer_Sambashare_RT.jpg)