import sys
from datetime import datetime
import os
import csv
import settings
import file_handler
import inspect
import script_manager
import pprint
def create_log(timestamp: str = None, filetype: str = None, log_name: str = None) -> str:

    if filetype != ".txt" and filetype != ".csv":
        print("If creating a log using logger(), you must input either '.txt' or '.csv' for param 'filetype'.")
        sys.exit(1)
    if log_name is None:
        print("If creating a log using logger(), you must input a name for the log using param 'log_name'. ")
        sys.exit(1)

    if timestamp is None:
        now: datetime = datetime.now()
        timestamp: str = now.strftime("%Y%m%d_%Hh%Mm%Ss")

    output_dir_filename: str = f"{log_name}_{timestamp}{filetype}"

    if script_manager.script_name_in_stack("nf_calc_MW.py"):
        log_parent_path = settings.NFB_LOG_DIR
    elif script_manager.script_name_in_stack("rifg_task.py"):
        log_parent_path = settings.RIFG_LOG_DIR
    else:
        log_parent_path = settings.DATA_DIR
        print(f"Could Not Find Any Main scripts in stack. Creating log in dir: {log_parent_path}")

    print(f"Pushing Files to: {log_parent_path}")
    output_log_path: str = os.path.join(log_parent_path, output_dir_filename)

    if filetype == ".csv":
        with open(output_log_path, 'w', newline='') as file:
            writer: csv.writer = csv.writer(file)
            writer.writerow([f"Created Output Log File: {output_log_path}"])
            print(f"Created Output Log File: {output_log_path}")

    elif filetype == ".txt":
        with open(output_log_path, 'w', newline='') as file:
            file.write(f"Created Output Log File: {output_log_path}")
            print(f"Created Output Log File: {output_log_path}")

    return output_log_path

def update_log(log_name: str, dictionary_to_write: dict = None, string_to_write: str = None):
    if log_name is None:
        print("for update_log(), param: 'log_name' must be provided if not creating a new log file.")
        sys.exit(1)

    if dictionary_to_write is None and string_to_write is None:
        print("for update_log(), please input data for either param: 'dictionary_to_write' or 'string_to_write'")
        sys.exit()

    if ".csv" in os.path.basename(log_name):
        pprint.pprint(dictionary_to_write)
        # Append data to an existing log file
        with open(log_name, 'a', newline='') as file:
            writer: csv.writer = csv.writer(file)
            for block_dicts in dictionary_to_write:
                if "block" in block_dicts:
                    writer.writerow([f"====== {block_dicts} ======"])
                    for in_block_key, in_block_value in dictionary_to_write[block_dicts].items():
                        if isinstance(in_block_value, dict) and "trial" in in_block_key:
                            writer.writerow([f"====== {in_block_key} ======"])
                            for trial_key, trial_value in in_block_value.items():
                                writer.writerow([trial_key, trial_value])
                        else:
                            writer.writerow([in_block_key, in_block_value])
                elif "whole_session_data" in block_dicts:
                    writer.writerow([f"====== whole_session_data ======"])
                    for param_key, param_value in dictionary_to_write["whole_session_data"].items():
                        writer.writerow([param_key, param_value])

                elif "trial" in block_dicts:  # for rifg data dictionary recording
                    print(f"writing trial")
                    writer.writerow([f"====== {block_dicts} ======"])
                    for trial_key, trial_value in dictionary_to_write[block_dicts].items():
                        writer.writerow([trial_key, trial_value])

    elif ".txt" in os.path.basename(log_name):
        with open(log_name, 'a', newline='') as file:
            file.write(string_to_write + "\n")

    return None

def print_and_log(string_to_write):
    log_name = file_handler.get_most_recent(action="txt_output_log")
    print(str(string_to_write))
    update_log(log_name=log_name, string_to_write=str(string_to_write))