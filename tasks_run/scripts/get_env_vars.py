import settings
import argparse
import os
import sys

def change_filepaths() -> list:
    return None

# Step 1: Create the argument parser
parser = argparse.ArgumentParser(description="Make environment variables from the variables assigned in the settings script")

# Step 2: Add input argument and verbose flag
parser.add_argument('action', help='What action to be performed')
parser.add_argument('input_vars', help='Name of variables to be used')
parser.add_argument('--verbose', '-v', action='store_true', help='Increase output verbosity')
parser.add_argument('--changefs', '-cfs', action='store_true', help="Change any input paths to thier paths on another filesystem.")

args = parser.parse_args()

if args.action == "print_value":
    if "," in args.input_vars:
        print("If you are using 'print_value' for the action argument, please input only one input variable.")
        sys.exit(1)
    else:
        # Check if the variable exists in the settings module
        if hasattr(settings, args.input_vars):
            ar_value = getattr(settings, args.input_vars)
            print(ar_value)
        else:
            raise Exception(f"Could not find the given input variable: {args.input_vars} in the settings file")
                
elif args.action == "make_env_variable":
    print("getting env var")
else:
    print(f"Invalid argument: {args.action} option for the action arguement. Valid options are 'print_value' or 'make_env_variable'")
    sys.exit(1)

# Step 3: Parse the arguments
args = parser.parse_args()
