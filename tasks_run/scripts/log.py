import sys
from datetime import datetime
import os
import csv
import settings
import FileHandler

def create_log(
           timestamp: str = None,
           filetype: str = None,
           log_name: str = None) -> str:

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
    log_parent_path = settings.NFB_LOG_DIR

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

def update_log(log_name: str, trial: int = None, dictionary_to_write: dict = None, string_to_write: str = None):
    if log_name is None:
        print("for update_log(), param: 'log_name' must be provided if not creating a new log file.")
        sys.exit(1)

    if dictionary_to_write is None and string_to_write is None:
        print("for update_log(), please input data for either param: 'dictionary_to_write' or 'string_to_write'")
        sys.exit()

    if ".csv" in os.path.basename(log_name):
        if trial is None:
            print("'trial' param is required when writing to a csv file in update_log()")
            sys.exit(1)
        # Append data to an existing log file
        with open(log_name, 'a', newline='') as file:
            writer = csv.writer(file)
            if trial is not None:
                writer.writerow([f"====== Trial: {trial} ======"])
            for key, value in dictionary_to_write.items():
                writer.writerow([key, value])

    elif ".txt" in os.path.basename(log_name):
        with open(log_name, 'a', newline='') as file:
            file.write(string_to_write + "\n")

    return None

def print_and_log(string_to_write):
    log_name = file_handler.get_most_recent(action="txt_output_log")
    print(str(string_to_write))
    update_log(log_name=log_name, string_to_write=str(string_to_write))