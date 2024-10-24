#!/bin/bash

# get chid and users from userfile path
user_info=$(grep $(whoami) "$user_file")
if [ $? -ne 0 ]; then
  echo "I could not find your chid and user name in the users file (${user_file})"
  echo "Please enter your information in that file like this:"
  echo ""
  echo "$(whoami), <your_child>"
  echo ""
  echo "then you can re-run this script"
  exit 1
fi
