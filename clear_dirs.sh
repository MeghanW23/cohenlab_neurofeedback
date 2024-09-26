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

directories_to_push=()