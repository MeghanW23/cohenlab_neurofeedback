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
## 3. Create a custom docker network
To set a static IP address for a Docker container, you need to use a custom Docker network. By default, Docker assigns dynamic IP addresses to containers, but you can create a custom network and specify a fixed IP within that network.

```
docker network create \
  --subnet=192.168.2.0/24 \
  samba_docker_network
```

`192.168.2.0/24`: This means that the network starts at 192.168.2.0, and it includes IPs from 192.168.2.1 to 192.168.2.254. The /24 subnet mask means the first 24 bits of the IP address are for the network, leaving the last 8 bits for host addresses.


## 4. Start Sambashare Service in Running Docker Container 
Run a container with ports exposed:
```
docker run -d \
    --name samba \
    --net samba_docker_network \
    --ip 192.168.2.6 \
    -p 139:139 \
    -p 445:445 \
    -v /Users/samba_user/sambashare:/sambashare \
    samba_nfb_docker:1.0 bash -c "service smbd start && tail -f /dev/null"
```
`--name`: Name of the docker container 

`-p 139:139`
- Host Port (139): The port on the host machine (your computer).
- Container Port (139): The port inside the container where the Samba service is running. Port 139 is typically used by NetBIOS over TCP/IP for file sharing, and it's often associated with SMB (Server Message Block) services.

`-p 1445:445:`
Host Port (1445): This is the port on the host machine.
Container Port (445): The port inside the container where Samba's SMB service runs. Port 445 is the default port used by SMB (and specifically for file sharing) on modern Windows and Unix-based systems.

`-v /Users/samba_user/sambashare:/sambashare`: Mount the sambashare directory to the container 

`samba_nfb_docker:1.0 bash -c "service smbd start && tail -f /dev/null"`: Run the container, start the sambashare service, and tail -f /dev/null so it continues to run

*NOTE: If port 445 on your machine is already allocated, try turning off mac's sambashare. Navigate to System Settings > Sharing, then under "File Sharing," turn off the "Share files and folders using SMB" option.*

You can check the ip of the running docker container via:
```
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container_name_or_id>
```

## 5. Connect from Remote Client
You will need to enter the following to connect:
1. The docker container's IP. On Mac and Linux, you can connect via both IP and port. Windows doesn't usually allow you to specify a port when using `\\<host_ip>\sambashare`. So, the Windows file explorer would try to connect on port 445 by default (not 1445).
2. The name of the exported sambashare directory (ex. `sambashare`)
3. A valid username and password

![MRI control computer sambashare configuration](https://github.com/MeghanW23/cohenlab_neurofeedback/blob/main/setup_samba_docker/MRI_Computer_Sambashare_RT.jpg)



###### More resources for learning about computer networks and port mapping:
[Crash Course: Computer Networks](https://www.youtube.com/watch?v=3QhU9jd03a0)

[Crash Course: The Internet](https://www.youtube.com/watch?v=AEaKrq3SpW8)

[Crash Course: The World Wide Web](https://www.youtube.com/watch?v=guvsH5OFizE&t=1s)

[Port configuration in docker container](https://www.youtube.com/watch?v=6by0pCRQdsI)
