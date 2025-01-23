#!/bin/bash
function check_ips {
    HOST_MACHINE_IP="$1"
    MRI_SCANNER_IP="$2"

    echo "Checking for correct IPs ..."
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

}
function boot_server {
    SAMBASHARE_MOUNT_DIR="$1"
    SMB_CONF_FILE_PATH="$2"
    SMB_COPY_FILES_SCRIPT="$3"

    echo "Starting Samba File Server..."
    docker run -d --rm \
    --name samba \
    -e TZ="America/New_York" \
    -e USER_UID=$(id -u $(whoami)) \
    -e USER_GID=$(id -g $(whoami)) \
    -e USER_NAME=smbuser \
    -p 139:139 \
    -p 445:445 \
    -p 137:137 \
    -p 138:138 \
    -v ${SAMBASHARE_MOUNT_DIR}:/samba_mount_to_mac \
    -v ${SMB_CONF_FILE_PATH}:/etc/samba/smb.conf \
    -v ${SMB_COPY_FILES_SCRIPT}:/$(basename ${SMB_COPY_FILES_SCRIPT}) \
    meghanwalsh/nfb_samba_share:latest bash -c "systemctl start smbd && systemctl enable smbd && python3 move_stuff_over.py &"

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
}
function stop_server {
    echo "Ok, killing running container ..."
    docker kill samba
    docker rm samba 
    echo "Done. You may now re-boot a new file server if desired."
}
function check_for_active_server {

    running_container=$(docker ps --filter "name=samba" --format "{{.Names}}")
    if [ -z "$running_container" ]; then 
        echo " " 
        echo "There are no running samba containers."
        
        stopped_containers=$(docker ps -a --filter "name=samba" --format "{{.Names}}")
        if [ ! -z "$stopped_containers" ]; then 
            echo "A stopped 'samba' container was detected. Please either restart it or kill it before choosing any additional server options."
            echo "To kill the container, run: "
            echo "  docker rm samba"
            read -p "Press any key to continue. "
            exit 1
        else 
            return 1
        fi
    elif [ "samba" = "$running_container" ]; then 
        samba_process=$(docker exec samba ps aux | grep -v grep | grep -i /usr/sbin/smbd)
        if [ -n "$samba_process" ]; then 
            echo "An active samba file server was found."
            return 0
        else 
            echo "Could not find an active samba file server."
            return 3
        fi 
    else
        echo "Something went wrong in the search for a matching docker container."
        return 2 
    fi 
}
function run_another_task {
    while true; do 
        read -p "Run another samba file server action? (y/n): " another_option
        if [ "$another_option" = "y" ]; then 
            return 0
        elif [ "$another_option" = "n" ]; then 
            return 1
        else 
            echo "Please enter either 'y' or 'n'"
        fi 
    done 
}

# Get param variables 
settings_script_path="$1"
automatic_version="$2"

# Get settings variables 
HOST_MACHINE_IP=$(python "$settings_script_path" HOST_MACHINE_IP -s)
MRI_SCANNER_IP=$(python "$settings_script_path" MRI_SCANNER_IP -s)
SAMBASHARE_MOUNT_DIR=$(python "$settings_script_path" SAMBASHARE_MOUNT_DIR -s)
SMB_CONF_FILE_PATH=$(python "$settings_script_path" SMB_CONF_FILE_PATH -s)
SMB_COPY_FILES_SCRIPT=$(python "$settings_script_path" SMB_COPY_FILES_SCRIPT -s)


if [ ! -d "$SAMBASHARE_MOUNT_DIR" ]; then 
    echo "Could not find the Sambashare Directory on Host Machine at: ${SAMBASHARE_MOUNT_DIR}"
    exit 1 
fi 

if [ "$automatic_version" = "true" ]; then 
    check_for_active_server
    status=$?
    if [ "$status" -eq 1 ]; then  
        while true; do 
            read -p "The Samba file server is not active. Boot it now? (y/n): " boot_option_automatic 
            if [ "$boot_option_automatic" = "y" ]; then
                boot_server "$SAMBASHARE_MOUNT_DIR" "$SMB_CONF_FILE_PATH" "$SMB_COPY_FILES_SCRIPT"
                break 
            elif [ "$boot_option_automatic" = "n" ]; then
                echo "Ok, not booting..."
                break 
            else 
                echo "Invalid option. Please enter either 'y' or 'n'"
            fi
        done
    elif [ "$status" -eq 3 ]; then  
        while true; do 
            read -p "The Samba file server is not active (but the docker container is). Kill and boot a new container now? (y/n): " boot_option_automatic 
            if [ "$boot_option_automatic" = "y" ]; then
                stop_server
                boot_server "$SAMBASHARE_MOUNT_DIR" "$SMB_CONF_FILE_PATH" "$SMB_COPY_FILES_SCRIPT"
                break 
            elif [ "$boot_option_automatic" = "n" ]; then
                echo "Ok, not re-booting. Continuing..."
                break 
            else 
                echo "Invalid option. Please enter either 'y' or 'n'"
            fi
        done 
    elif [ "$status" -eq 2 ]; then  
        read -p "Press any key to continue. "
    fi 
    exit 0 
fi 

# Choose options 
while true; do 
    echo " "
    echo "Samba File Server Options: "
    echo "(1) Check Host and MRI IPs"
    echo "(2) Start/Stop the File Server"
    echo "(3) Check if the Server is Active"
    read -p "Please choose the number associated with the action you want to run: " option
    echo " " 
    if [ "$option" = "1" ]; then 
        echo "Ok, Checking Host and MRI IPs."

        check_ips "$HOST_MACHINE_IP" "$MRI_SCANNER_IP"

        run_another_task
        status=$?
        if [ "$status" -eq 0 ]; then
            echo "Ok, running another task ..."
        elif [ "$status" -eq 1 ]; then
            echo "Ok, exiting ..."
            break
        fi 

    elif [ "$option" = "2" ]; then 
        check_for_active_server
        server_status=$?
        if [ "$server_status" -eq 1 ]; then
            while true; do 
                read -p "No active file servers found. Start a new file server? (y/n): " boot_option
                if [ "$boot_option" = "y" ]; then 
                    boot_server "$SAMBASHARE_MOUNT_DIR" "$SMB_CONF_FILE_PATH" "$SMB_COPY_FILES_SCRIPT"
                    break
                elif [ "$boot_option" = "n" ]; then 
                    echo "Ok, not booting server."
                    break
                else 
                    echo "Please choose either 'y' or 'n'."
                fi
            done             
        elif [ "$server_status" -eq 0 ] || [ "$server_status" -eq 3 ]; then
            while true; do 
                read -p "A running samba docker container was found. Kill the container? (y/n): " kill_option
                if [ "$kill_option" = "y" ]; then 
                    stop_server
                    break 
                elif [ "$kill_option" = "n" ]; then 
                    echo "Ok, not killing container."
                    
                    break 
                else
                    echo "Please enter either 'y' or 'n'."
                fi 
            done 
        else 
            echo " " 
            echo "To BOOT a NEW file server, there must be:"
            echo "  (1) NO already active samba file servers" 
            echo "  (2) NO running docker containers with the name 'samba'"
            echo "  Once the above conditions are met, please re-try booting the file server again."
            echo "To KILL an ALREADY EXISTING file server and/or container, there must be:"
            echo "  (1) A running docker container. " 
            echo "  (2) The samba server does NOT have to be active "
            echo "  Once the above conditions are met, please re-try killing the file server again."
            echo " " 
        fi 

        run_another_task
        status=$?
        if [ "$status" -eq 0 ]; then
            echo "Ok, running another task ..."
        elif [ "$status" -eq 1 ]; then
            echo "Ok, exiting ..."
            break
        fi 

    elif [ "$option" = "3" ]; then 
        check_for_active_server

        run_another_task
        status=$?
        if [ "$status" -eq 0 ]; then
            echo "Ok, running another task ..."
        elif [ "$status" -eq 1 ]; then
            echo "Ok, exiting ..."
            break
        fi 
    else 
        echo "Invalid option. Please chose a valid integer option."
    fi 
done 