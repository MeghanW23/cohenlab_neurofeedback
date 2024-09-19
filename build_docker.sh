#!/bin/bash

REPO_URL="https://github.com/MeghanW23/cohenlab_neurofeedback"
username="$(whoami)"
user_file="/workdir/users.txt"

echo "Pulling Any New Changes to the Repo..."
git pull origin main

# Build the Docker image
echo "Building Docker image..."
sudo docker build -t nfb_docker:1.0 .

echo "Making Docker Runner Executable..."
for file in $(pwd)/run_docker_container*
do 
    sudo chmod +x "$file"
done 

echo "Making All Other Necessary Scripts Executable ..."
sudo chmod +x startup_docker.sh
sudo chmod +x ssh_e3.sh

echo "Adding your username to docker records, if not already added ... "
if ! grep -q "$username" "$user_file"; then

  while true; do
    read -p "Please Enter Your CD ID: " chid

    if ! echo "$chid" | grep -q "ch"; then
      echo "Please Assure Your CH ID includes 'ch'"

    else
      echo "ok, Using CH ID: ${chid}"
      echo "user_${username} = (${username}, ${chid})" >> "$user_file"
      echo "Your User Information is added to ${user_file}:"
      grep $username $user_file

      break
    fi
  done
else
  echo "Your User Information is already added:"
  grep $username $user_file
fi

echo "All Set!"
echo "Run script: run_docker_container.sh to run the docker image"
