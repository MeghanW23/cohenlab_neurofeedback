### Step one: 
Run the Docker Containter 

### Step Two:
Create Keypair for docker/e3 connection: ``` ssh-keygen -t rsa -f /workdir/.ssh/docker_e3_key_$CHID -C "for e3 passwordless login via docker" ```

### Step Three 
Copy Public Key to E3: ``` ssh-copy-id -i /workdir/.ssh/docker_e3_key_$CHID.pub $CHID@e3-login.tch.harvard.edu ```


### Step Four
4a. Open Config File: ``` sudo nano /workdir/.ssh/config ```

4b. Edit Config File:
```
Host e3
    HostName e3-login.tch.harvard.edu
    User $CHID
    IdentityFile ~/.ssh/docker_e3_key
    ForwardAgent yes
    ForwardX11 yes
    ForwardX11Trusted yes
```
