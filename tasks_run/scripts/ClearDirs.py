#!/bin/bash
echo "This script clears directories that store data not needed past script runtime"

directories_to_clear=(
$(python -c "from settings import TMP_OUTDIR_PATH; print(TMP_OUTDIR_PATH)")
)

for dir in "${directories_to_check[@]}"; do
  while true; do
    read -p "Clear this dir: ${dir}? (y/n): " clear_dir_choice
    if [ "$clear_dir_choice" == "y" ]; then
      echo "Ok, Clearing this dir."
      rm -rf "$dir"/*
      echo "Cleared Dir."
      break
    elif [ "$clear_dir_choice" == "n" ]; then
      echo "Ok, Not Clearing Dir."
      break
    else
      echo "Please choose either 'y' or 'n'."
    fi
  done
done

path_to_e3_subj_space_masks="/lab-share/Neuro-Cohen-e2/Public/notebooks/mwalsh/ADHD_Stimulants_Data/subj_space_masks"
while true; do
  read -p "send subj-space masks to e3? (y/n): " send_to_e3
  if [ $send_to_e3 == "y" ]; then
    echo "Ok, sending to e3 ..."

    break
  elif [ $send_to_e3 == "n"]; then


  fi
