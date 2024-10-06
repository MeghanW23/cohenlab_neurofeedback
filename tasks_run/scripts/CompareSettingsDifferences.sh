#!/bin/bash

e3_settings=$(python -c 'from settings import E3_PATH_TO_SETTINGS; print(E3_PATH_TO_SETTINGS)')
e3_hostname=$(python -c 'from settings import E3_HOSTNAME; print(E3_HOSTNAME)')
private_key=$(python -c 'from settings import LOCAL_PATH_TO_PRIVATE_KEY; print(LOCAL_PATH_TO_PRIVATE_KEY)')

echo -e "\nComparing: $e3_settings to $DOCKER_PATH_TO_SETTINGS\n"


# Show the differences and store the output
differences=$(ssh -i "$private_key" "$CHID@${e3_hostname}" "diff ${e3_settings} -" < "$DOCKER_PATH_TO_SETTINGS" 2>/dev/null)
if [ "$differences" = "" ]; then
  echo "---------------------------------"
  echo "NO DIFFERENCES DETECTED"
else
  echo "DIFFERENCES DETECTED: "
  echo "  > means in docker script"
  echo "  < means in e3 script"
  echo "---------------------------------"
  echo "$differences"
fi
echo "---------------------------------"