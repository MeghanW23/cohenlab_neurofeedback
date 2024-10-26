#!/bin/bash

echo -e "\nComparing: $E3_SETTINGS to $LOCAL_SETTINGS\n"


# Show the differences and store the output
differences=$(ssh -i "$PRIVATE_KEY" "$CHID@${E3_HOSTNAME}" "diff ${E3_SETTINGS} -" < "$LOCAL_SETTINGS" 2>/dev/null)
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