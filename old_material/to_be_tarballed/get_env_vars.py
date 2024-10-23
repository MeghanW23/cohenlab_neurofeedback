# import settings
import argparse
import os
import sys
import subprocess

# get settings from script dir 
sys.path.append(os.path.dirname(os.getcwd()))
import settings

def change_filepaths() -> list:
    return None

# Step 1: Create the argument parser
parser = argparse.ArgumentParser(description="Make environment variables from the variables assigned in the settings script")

# Step 2: Add input argument and verbose flag
parser.add_argument('input_var', help='Name of variable to be used')
parser.add_argument('--changefs', '-cfs', action='store_true', help="Change any input paths to thier paths on another filesystem.")

args = parser.parse_args()

if hasattr(settings, args.input_var):
    ar_value = getattr(settings, args.input_var)
    print(ar_value)
else:
    raise Exception(f"Could not find the given input variable: {args.input_var} in the settings file")

if args.changefs:
    