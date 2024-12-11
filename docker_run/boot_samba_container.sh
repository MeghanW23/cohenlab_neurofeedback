#!/bin/bash
settings_script_path="$(dirname $(dirname "$(realpath "$0")"))/tasks_run/scripts/settings.py"
HOST_MACHINE_IP=$(python "$settings_script_path" HOST_MACHINE_IP -s)
MRI_SCANNER_IP=$(python "$settings_script_path" MRI_SCANNER_IP -s)
LOCAL_SAMBASHARE_DIR_PATH=$(python "$settings_script_path" LOCAL_SAMBASHARE_DIR_PATH -s)
if [ ! -d "$LOCAL_SAMBASHARE_DIR_PATH" ]; then 
    echo "Could not find the Sambashare Directory on Host Machine at: ${LOCAL_SAMBASHARE_DIR_PATH}"
    exit 1 
fi 

echo "The expected host machine IP address is: ${HOST_MACHINE_IP}"
echo "Looking for the expected IP of the host machine ..."

echo "IP addresses (IPv4 or IPv6) associated with the network interface of your system (127.0.0.1): "
ip_addresses=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}')
echo "${ip_addresses}"
if echo "$ip_addresses" | grep -q "$HOST_MACHINE_IP"; then 
    echo "Expected Host Machine IP was found. Continuing..."
    sleep 0.5
else
    echo " " 
    echo "WARNING: the expected host machine IP (${HOST_MACHINE_IP}) was not found in the current list of IP addresses associated with the network interface of your system"
    echo "The MRI may not be able to connect to this computer's Samba file server." 
    echo " " 
    read -p "Press any key to continue. "
    
fi 

echo "The expected MRI Scanner IP address is: ${MRI_SCANNER_IP}"
echo "Pinging the MRI Scanner now ..."
if ping -c 5 "$MRI_SCANNER_IP" &> /dev/null; then
    echo "Ping to MRI Scanner was successful. Continuing ..."
else
    echo " " 
    echo "WARNING: Ping to MRI Scanner failed."
    echo "The MRI may not be able to connect to this computer's Samba file server." 
    echo " " 
    read -p "Press any key to continue. "
fi

echo "Starting Samba File Server..."
docker run -d \
--name samba \
-p 139:139 \
-p 445:445 \
-v ${LOCAL_SAMBASHARE_DIR_PATH}:/sambashare \
meghanwalsh/nfb_samba_share:latest bash -c "systemctl start smbd && tail -f /dev/null"

# Check if the docker run command failed
if [ $? -ne 0 ]; then
    echo "Docker run command failed. Please examine any error messages that may be printed out above."
    echo "The MRI may not be able to connect to this computer's Samba file server." 
    read -p "Press any key to continue. "
else
    echo "Docker run command was successful. Checking if the file server is running..."
    if docker exec "samba" ps aux | grep -v grep | grep smbd > /dev/null 2>&1; then
        echo "Samba service is running. Continuing ..."
    else
        echo "Samba service is not running."
        echo "The MRI may not be able to connect to this computer's Samba file server." 
        read -p "Press any key to continue. "
    fi
fi