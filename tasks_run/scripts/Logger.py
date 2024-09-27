import sys
from datetime import datetime
import os
import csv
import settings
import FileHandler
import ScriptManager


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

    if ScriptManager.script_name_in_stack(settings.NFB_SCRIPT_NAME):
        log_parent_path = settings.NFB_LOG_DIR
    elif ScriptManager.script_name_in_stack(settings.RIFG_SCRIPT_NAME):
        log_parent_path = settings.RIFG_LOG_DIR
    elif ScriptManager.script_name_in_stack(settings.MSIT_SCRIPT_NAME_PRE):
        log_parent_path = settings.MSIT_LOG_DIR
    elif ScriptManager.script_name_in_stack(settings.MSIT_SCRIPT_NAME_POST):
        log_parent_path = settings.MSIT_LOG_DIR
    elif ScriptManager.script_name_in_stack(settings.LOCALIZER_FILE_NAME):
        log_parent_path = settings.LOCALIZER_LOG_DIR
    else:
        log_parent_path = settings.DATA_DIR_PATH
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
        # Append data to an existing log file
        with open(log_name, 'a', newline='') as file:
            writer: csv.writer = csv.writer(file)
            for block_dicts in dictionary_to_write:
                if "whole_session_data" in block_dicts:
                    writer.writerow([f"====== whole_session_data ======"])
                    for param_key, param_value in dictionary_to_write["whole_session_data"].items():
                        writer.writerow([param_key, param_value])

                if "block" in block_dicts:
                    writer.writerow([f"====== {block_dicts} ======"])
                    for in_block_key, in_block_value in dictionary_to_write[block_dicts].items():
                        if not isinstance(in_block_value,
                                          dict):  # put all the block-level vars in one place, at the top of this block's csv section
                            writer.writerow([in_block_key, in_block_value])

                    for in_block_key, in_block_value in dictionary_to_write[block_dicts].items():  # then, get the trials
                        if isinstance(in_block_value, dict) and "trial" in in_block_key:
                            writer.writerow([f"====== {in_block_key} ======"])
                            for trial_key, trial_value in in_block_value.items():
                                writer.writerow([trial_key, trial_value])

                elif "trial" in block_dicts:  # for rifg data dictionary recording
                    writer.writerow([f"====== {block_dicts} ======"])
                    for trial_key, trial_value in dictionary_to_write[block_dicts].items():
                        writer.writerow([trial_key, trial_value])

    elif ".txt" in os.path.basename(log_name):
        with open(log_name, 'a', newline='') as file:
            file.write(string_to_write + "\n")

    return None


def print_and_log(string_to_write):
    log_name = FileHandler.get_most_recent(action="txt_output_log")
    print(str(string_to_write))
    update_log(log_name=log_name, string_to_write=str(string_to_write))