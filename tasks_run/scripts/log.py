import sys
from datetime import datetime
import os
import csv
import settings

def create_log(
           timestamp: str = None,
           filetype: str = None,
           log_name: str = None,
           path_to_log: str = None) -> str:

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
    log_parent_path = settings.LOGGING_DIR_PATH

    output_log_path: str = os.path.join(log_parent_path, output_dir_filename)

    if filetype == ".csv":
        with open(output_log_path, 'w', newline='') as file:
            writer: csv.writer = csv.writer(file)
            writer.writerow([f"Created Output Log File: {output_log_path}"])
            print(f"Created Output Log File: {output_log_path}")

    else:
        with open(output_log_path, 'w', newline='') as file:
            file.write(f"Created Output Log File: {output_log_path}")
            print(f"Created Output Log File: {output_log_path}")

    return output_log_path
