### Step one: 
Create Keypair for docker/e3 connection: ``` ssh-keygen -t rsa -f /Users/<username>/.ssh/docker_e3_key -C "for e3 passwordless login via docker" ```

### Step Two:
Copy Public Key to E3: ``` ssh-copy-id -i /Users/<username>/.ssh/docker_e3_key.pub chID@e3-login.tch.harvard.edu ```


### Step Three 
3a. Open Config File: ``` sudo nano /Users/<username>/.ssh/config ```

3b. Edit Config File:
```
Host e3
    HostName e3-login.tch.harvard.edu
    User $CHID
    IdentityFile ~/.ssh/docker_e3_key
    ForwardAgent yes
    ForwardX11 yes
    ForwardX11Trusted yes
```
