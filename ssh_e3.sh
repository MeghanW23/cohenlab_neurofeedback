#!/bin/bash

if [ "$USERNAME" = "meghan" ]; then
    chid="ch246081"
elif [ "$USERNAME" = "sofiaheras" ]; then
    chid="ch261487"
else
    echo "Your username has not been configured for e3 ssh via this script. Please add your ch id or see meghan"
    exit 1
fi

echo "Using CH ID: $chid"
echo "Ssh-ing into E3 ... "
ssh -XYC ${chid}@e3-login.tch.harvard.edu