import sys
from datetime import datetime
import os
import csv
import settings
import FileHandler
import ScriptManager
from typing import List, Optional

def get_log_dir() -> str:
    if ScriptManager.script_name_in_stack(settings.NFB_SCRIPT_NAME):
        log_parent_path = settings.NFB_LOG_DIR
    elif ScriptManager.script_name_in_stack(settings.RIFG_SCRIPT_NAME):
        log_parent_path = settings.RIFG_LOG_DIR
    elif ScriptManager.script_name_in_stack(settings.MSIT_SCRIPT_NAME):
        log_parent_path = settings.MSIT_LOG_DIR
    elif ScriptManager.script_name_in_stack(settings.LOCALIZER_FILE_NAME):
        log_parent_path = settings.LOCALIZER_LOG_DIR
    elif ScriptManager.script_name_in_stack(settings.REST_SCRIPT_NAME):
        log_parent_path = settings.REST_LOG_DIR
    else:
        log_parent_path = settings.DATA_DIR_PATH
        print(f"Could Not Find Any Main scripts in stack. Creating log in dir: {log_parent_path}")

    return log_parent_path

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
    log_parent_path = get_log_dir()
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
    log_dir = get_log_dir()
    log_name = FileHandler.get_most_recent(action="txt_output_log", log_dir=log_dir)
    print(str(string_to_write))
    update_log(log_name=log_name, string_to_write=str(string_to_write))
    
def update_score_csv(action: str, 
                     task:str, 
                     path_to_csv_dir:str=None, 
                     path_to_csv:str=None, 
                     pid:str=None, 
                     score = None, 
                     tr: int = None,
                     additional_headers: List[str] = None,
                     additional_data: list = None) -> Optional[str]: 
    options: dict = {
        "action_options": ["create_csv", "add_to_csv"],
        "task_options": ["rifg", "nfb", "msit"],
        "score_options": {
            "nfb": [-1, 1],
            "rifg": ["hit", "miss", "correct_rejection", "false_alarm"],
            "msit": ["correct", "incorrect", "invalid_press", "no_press"]
        },
        "csv_headers": {
            "nfb": ["TR", "ActivationScore"],
            "rifg": ["TR", "TrialResult"],
            "msit": ["TR", "TrialResult"]
        }
    }
        
    # Catch errrors 
    if task not in options["task_options"]:
        print(f"Inputted task argument for score_csv_maker(): '{task}' is not a valid option. The valid options are: ")
        for i in options["task_options"]: print(f"   {i}")
        sys.exit(1)
    elif action not in options["action_options"]: 
        print(f"Inputted action argument for score_csv_maker(): {action} is not a valid option. The valid options are: ")
        for i in options["action_options"]: print(f"   {i}")
        sys.exit(1)
    else: 
        if action == options["action_options"][0]:
            if pid is None: 
                print(f"A pid must be provided if score_csv_maker()'s action argument is: {options['action_options'][0]}.")
                sys.exit(1)
            elif path_to_csv_dir is None: 
                print(f"A path_to_csv_dir must be provided if score_csv_maker()'s action argument is: {options['action_options'][0]}.")
                sys.exit(1)
            elif additional_headers is not None and not isinstance(additional_headers, list):
                print("If using the 'additional_headers' param, the inputted object value must be type: list")
                sys.exit(1)
            elif additional_data is not None:
                print(f"param: 'additional_data' must NOT be used if score_csv_maker()'s action argument is: {options['action_options'][0]}.")
                sys.exit(1)
        elif action == options["action_options"][1]:
            if path_to_csv_dir is not None:
                print(f"'path_to_csv_dir' must only be provided if score_csv_maker()'s action argument is: {options['action_options'][0]}.")
                sys.exit(1)
            elif path_to_csv is None:
                print(f"An existing 'path_to_csv' must be provided if score_csv_maker()'s action argument is: {options['action_options'][1]}.")
                sys.exit(1)
            elif not os.path.exists(path_to_csv) or not path_to_csv.endswith(".csv"):
                print(f"An existing path to the score csv file must be provided if score_csv_maker()'s action argument is: {options['action_options'][1]}.")
                print(f"Inputted path: {path_to_csv} is not a valid CSV file.")
                sys.exit(1)
            elif tr is None or not isinstance(tr, int):
                if tr is None: 
                    print(f"the Trial's TR must be given (using param: 'tr') if score_csv_maker()'s action argument is: {options['action_options'][1]}")
                    sys.exit(1)
                else:
                    print(f"the Trial's TR must be an int value (using param: 'tr') if score_csv_maker()'s action argument is: {options['action_options'][1]}")
                    sys.exit(1)
                print(f)
            elif score is None:
                print(f"A score must be provided if score_csv_maker()'s action argument is: {options['action_options'][1]}.")
                sys.exit(1)
            elif additional_data is not None and not isinstance(additional_data, list):
                print("If using the 'additional_data' param, the inputted object value must be type: list")
                sys.exit(1)
            elif additional_headers is not None:
                print(f"param: 'additional_headers' must NOT be used if score_csv_maker()'s action argument is: {options['action_options'][1]}.")
                sys.exit(1)
            else:
                if task == "nfb":
                    if score < options["score_options"][task][0] or score > options["score_options"][task][1]:
                        print(f"When runnning task: '{task}' for func score_csv_maker(), 'score' must be within the range of {options['score_options'][task][0]} to {options['score_options'][task][1]}")
                elif score not in options["score_options"][task]:
                    print(f"When runnning task: '{task}' for func score_csv_maker(), 'score' must equal one of the following options:")
                    for i in options["score_options"][task]: print(f"   {i}")
                    print(f"and you gave score: {score}")
                    sys.exit(1)
    
    # Proceed based on inputted action (0 = create csv, 1 = add to csv)
    if action == options["action_options"][0]:
        # make CSV filepath
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        csv_filename = f"{pid}_{task}_scores_{timestamp}.csv"
        path_to_csv = os.path.join(path_to_csv_dir, csv_filename)

        # lookup headers based on path 
        headers = [options["csv_headers"][task][0], options["csv_headers"][task][1]]
        if additional_headers is not None:
            for header in additional_headers:
                headers.append(header)

        with open(path_to_csv, "w") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

        print(f"Created Score CSV file at: {path_to_csv}")
        return path_to_csv
    
    elif action == options["action_options"][1]:
        data_to_add = [tr, score]
        if additional_data is not None:
            for value in additional_data:
                data_to_add.append(value)
        with open(path_to_csv, "a") as f:
            writer = csv.writer(f)
            writer.writerow(data_to_add)