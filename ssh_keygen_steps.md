### Step One: 
Run the Docker Containter 

### Step Two: 
Set Permissions for Folder:
``` chmod 700 /workdir/.ssh ```
``` chmod 600 /workdir/.ssh/docker_e3_key_$CHID ```
``` chmod 644 /workdir/.ssh/docker_e3_key_$CHID.pub ```
``` chmod 600 /workdir/.ssh/config_$CHID ```

### Step Three:
Create Keypair for docker/e3 connection: ``` ssh-keygen -t rsa -f /workdir/.ssh/docker_e3_key_$CHID -C "for e3 passwordless login via docker for '${CHID}'" ```

### Step Four: 
Copy Public Key to E3: ``` ssh-copy-id -i /workdir/.ssh/docker_e3_key_$CHID.pub $CHID@e3-login.tch.harvard.edu ```

### Step Five:
5a. Create User-Specific Config File: ``` sudo nano /workdir/.ssh/config_$CHID ```

5b. Add to Config File:
```
Host e3
    HostName e3-login.tch.harvard.edu
    User $CHID
    IdentityFile ~/.ssh/docker_e3_key_$CHID
    ForwardAgent yes
    ForwardX11 yes
    ForwardX11Trusted yes
```
