#!/bin/bash

set -e

echo "Registering ROI mask to participant data via local fnirt script"

while true; do
  echo "What ROI Mask Would You Like to Register? "
  echo "(1) ACC Mask"
  echo "(2) Motor Mask"
  echo "(3) RIFG Mask"

  read -p "Enter '1', '2', or '3': " choice

  if [ $choice = "1" ]; then
    echo "Ok, Registering ACC Mask"
    roi_mask=$(python3 -c "from settings import MNI_ACC_MASK_PATH; print(MNI_ACC_MASK_PATH)")
    echo "Using MNI ACC Mask at: $roi_mask"

    break
  elif [ $choice = "2" ]; then
    echo "Ok, Registering Motor Mask"
    roi_mask=$(python3 -c "from settings import MNI_MOTOR_MASK_PATH; print(MNI_MOTOR_MASK_PATH)")
    echo "Using MNI Motor Mask at: $roi_mask"
    break

  elif [ $choice = "3" ]; then
    echo "Ok, Registering RIFG Mask"
    roi_mask=$(python3 -c "from settings import MNI_RIFG_MASK_PATH; print(MNI_RIFG_MASK_PATH)")
    echo "Using MNI RIFG Mask at: $roi_mask"
    break

  else
    echo "Please choose either 1, 2, or 3"
  fi
done