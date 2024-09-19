#!/bin/bash

echo "Using CH ID: '${CHID}'"
echo "Ssh-ing into E3 ... "
ssh -XYC ${CHID}@e3-login.tch.harvard.edu