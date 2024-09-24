#!/bin/bash

set -e

REPO_URL="https://github.com/MeghanW23/cohenlab_neurofeedback"
username="$(whoami)"
user_file="./users.txt"

while true; do
  read -p "Pulling Any New Changes to the Repo First? (y/n): " choice
  if [ $choice = "y" ]; then
    echo "Ok, Pulling Now ..."
    git fetch
    git pull origin main
    break

  elif [ $choice = "n" ]; then
    echo "Ok, will not pull new changes"
    break

  else
    echo "Please choose either y or n"
  fi
done

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
sudo chmod +x get_ssh_keys.sh
sudo chmod +x make_venv.sh
sudo chmod +x tasks_run/scripts/RegisterFnirt.sh
sudo chmod +x tasks_run/scripts/TransferFilesE3.sh

echo "Adding your username to docker records, if not already added ... "
if ! grep -q "$username" "$user_file"; then

  while true; do
    read -p "Please Enter Your CD ID: " chid

    if ! echo "$chid" | grep -q "ch"; then
      echo "Please Assure Your CH ID includes 'ch'"

    else
      echo "ok, Using CH ID: ${chid}"
      echo "${username}, ${chid}" >> "$user_file"
      echo "Your User Information is added to ${user_file}:"
      grep $username $user_file

      break
    fi
  done
else
  echo "Your User Information is already added:"
  grep $username $user_file
fi

echo "Checking for the existence of the Python virtual environment ..."
if [ ! -d "venv/" ]; then
  while true; do
    read -p "Python virtual environment not found. Create? (y/n) " create_choice
    if [ "$create_choice" = 'y' ]; then
      echo "Ok, creating virtual environment now ..."
      ./make_venv.sh
      break
    else
      echo "Ok, I won't create the virtual environment. You can create it later by running the script: ./make_venv.sh"
      break
    fi
  done

else
  echo "Python virtual environment already created."
fi


echo "All Set!"
echo "Run script: run_docker_container.sh to run the docker image"
