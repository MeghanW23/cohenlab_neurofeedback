echo "Docker Private Key Path: $DOCKER_SSH_PRIVATE_KEY_PATH"
echo "CHID: $CHID"
echo "E3 Hostname: $E3_HOSTNAME"
echo "Username: $USER"
echo "E3 Settings.py Path: $E3_PATH_TO_SETTINGS"
echo "E3 Private Key Path: $E3_PRIVATE_KEY_PATH"
echo "ROI Mask Dir Path: $LOCAL_MASK_DIR_PATH"
echo "E3 Startup Registration Path: $E3_SETUP_REG_AND_COMPUTE_PATH"
echo "Local Sambashare Dir Path: $LOCAL_SAMBASHARE_DIR_PATH"
echo "PID List File: $PID_LIST_FILE"

while true 
do
    # input the pid 
    read -p "Enter Participant ID: " pid

    pid=$(echo "$pid" | xargs | tr '[:upper:]' '[:lower:]') # trim leading and trailing spaces

    # validate the PID format
    if [[ ! "$pid" =~ ^p[0-9]{3}$ ]]; then
        echo "Invalid Participant ID format. It must start with 'p' followed by three digits (e.g., p001)."
        continue
    fi

    # read pid list line by line
    found_pid=false
    if [[ -f "$PID_LIST_FILE" ]]; then
        while IFS= read -r line || [[ -n "$line" ]]; do
            # trim leading and trailing spaces
            line=$(echo "$line" | xargs)

            # skip empty lines
            if [[ -z "$line" ]]; then
                continue
            fi

            if [[ "$pid" == "$line" ]]; then
                found_pid=true
            fi

        done < "$PID_LIST_FILE"
    else
        echo "File $PID_LIST_FILE does not exist. Continuing with manual entry only."
    fi

    if [ "$pid" == "p999" ]; then 
        echo "Using Testing Participant ID ${pid}"
        break
    elif [[ "$found_pid" == false ]]; then
        echo "Using New Participant ID: ${pid}"

        # write PID to list 
        echo "" >> "$PID_LIST_FILE"
        echo "$pid" >> "$PID_LIST_FILE"

        break
    else
        get_new_pid=false

        echo "Found Already Existing Participant ID: ${pid}"
        while true 
        do 
            echo "Select from the following options:"
            echo "(1) Get a New Participant ID - NEW PARTICIPANTS ONLY"
            echo "(2) Using the Testing ID p999"
            echo "(3) Continue With the Already Existing Participant ID - CONTINUING PARTICIPANTS ONLY"
            read -p "Select an Option (1/2/3): " option

            # Validate input
            if [[ "$option" == "1" ]]; then 
                get_new_pid=true
                break 

            elif [[ "$option" == "2" ]]; then 
                pid="p999"
                break

            elif [[ "$option" == "3" ]]; then 
                break
            else

                echo "Please enter either 1, 2, or 3"
            fi 
        done 
        
        if [[ "$get_new_pid" == false ]]; then 
            break
        fi
    fi
done

echo "Using Participant ID: ${pid}"

echo "Starting SSH Now..."
ssh -t -i "$DOCKER_SSH_PRIVATE_KEY_PATH" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "${CHID}@${E3_HOSTNAME}" \
    "export USER='$USER' && \
    export CHID='$CHID' && \
    export E3_PATH_TO_SETTINGS='$E3_PATH_TO_SETTINGS' && \
    export E3_PRIVATE_KEY_PATH='$E3_PRIVATE_KEY_PATH' && \
    export LOCAL_MASK_DIR_PATH='$LOCAL_MASK_DIR_PATH' && \
    export LOCAL_SAMBASHARE_DIR_PATH='$LOCAL_SAMBASHARE_DIR_PATH' && \
    export PID='$pid' && \
    bash '$E3_SETUP_REG_AND_COMPUTE_PATH'"