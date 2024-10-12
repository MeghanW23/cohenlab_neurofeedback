#!/bin/bash

# create python virtual environment, if it doesnt already exist
echo "Checking for the existence of the Python virtual environment ..."
requirements="/workdir/run_container/python_requirements.txt"
if [ ! -d "venv/" ]; then
  python3 -m venv venv
  source venv/bin/activate
  pip install -r "$requirements"

else
  echo "Found Python virtual environment successfully."
fi

