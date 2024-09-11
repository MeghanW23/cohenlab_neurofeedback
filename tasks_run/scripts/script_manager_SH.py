import settings
import log_SH
import traceback
from datetime import datetime
from typing import Union, Tuple
import sys
import os
import time
import calculations_SH
import inspect
import file_handler

def retry_if_error(dictionary: dict):
    def decorator(func):
        def wrapper(*args, **kwargs):
            num_retries: int = settings.RETRIES_BEFORE_ENDING
            retries_left: int = num_retries
            current_block, current_trial = dict_get_most_recent(dictionary=dictionary, get="both")

            while retries_left >= 0:
                try:
                    if "this_trial_tries" not in dictionary[current_block][current_trial]:
                        dictionary[current_block][current_trial]["this_trial_tries"]: int = 1
                    else:
                        dictionary[current_block][current_trial]["this_trial_tries"] += 1

                    updated_dictionary = func(*args, **kwargs)

                    log_SH.print_and_log("Inter-Trial Calculations Successful.")
                    dictionary[current_block][current_trial]["successful_trial_end"]: bool = True
                    return updated_dictionary  # Return the result if successful

                except Exception as e:
                    # Print Error To User and Terminal Printout Log
                    log_SH.print_and_log("Error:")
                    log_SH.print_and_log(e)
                    traceback_str = traceback.format_exc()
                    log_SH.print_and_log(traceback_str)

                    # Record Time of Error
                    now: datetime = datetime.now()
                    string_time: str = now.strftime("%Y%m%d_%Hh%Mm%Ss")

                    if retries_left <= settings.TRIES_BEFORE_NEW_DCM:
                        log_SH.print_and_log("Getting New Dicom Instead...")
                        wait_for_new_dicom(dictionary=dictionary)

                    # Send Error Information To Dictionary Log
                    if "errors" not in dictionary[current_block][current_trial]:
                        dictionary[current_block][current_trial]["errors"]: list = []

                    info_for_log: tuple[str:str] = f"time_of_error: {string_time}", traceback_str
                    dictionary[current_block][current_trial]["errors"].append(info_for_log)

                    if "num_trials_with_errors" not in dictionary[current_block]:
                        dictionary[current_block]["num_trials_with_errors"]: int = 1
                    else:
                        dictionary[current_block]["num_trials_with_errors"] += 1


                    if retries_left == 0:
                        log_SH.print_and_log("Ran out of retries. Skipping this trial.")

                        dictionary[current_block]["num_trials_failed"] += 1

                        dictionary[current_block][current_trial]["successful_trial_end"]: bool = False

                        return dictionary  # Return None or handle as needed

                    log_SH.print_and_log(f"Retries left: {retries_left}")
                    retries_left = retries_left - 1

        return wrapper

    return decorator

def dict_get_most_recent(dictionary: dict, get: str) -> Union[str, Tuple[str, str]]:

    if get != "block" and get != "trial" and get != "both":
        log_SH.print_and_log(f"Invalid option for param: 'get' in function: dict_get_most_recent")
        sys.exit(1)

    # Filter block keys from the session data
    block_keys: list = [key for key in dictionary if key.startswith("block")]

    # Extract the numeric part of the block keys and find the most recent one
    most_recent_block_key: str = max(block_keys, key=lambda x: int(x.replace('block', '')))

    if get == "block":
        return most_recent_block_key

    trial_keys: list = [key for key in dictionary[most_recent_block_key] if key.startswith("trial")]
    most_recent_trial_key: str = max(trial_keys, key=lambda x: int(x.replace('trial', '')))

    if get == "trial":
        return most_recent_trial_key

    elif get == "both":
        return most_recent_block_key, most_recent_trial_key

def wait_for_new_dicom(dictionary: dict) -> dict:

    # special keyboard interrupt handling due to time_sleep disrupting the outer scope 'except' catcher
    log_SH.print_and_log("Waiting For New File ...")
    current_count: int = len(os.listdir(dictionary["whole_session_data"]["dicom_dir_path"]))
    last_logged_count: int = dictionary["whole_session_data"]["dicoms_in_dir"]

    while True:
        if current_count != last_logged_count:
            log_SH.print_and_log("New File Found In Dir...")
            dictionary["whole_session_data"]["dicoms_in_dir"]: int = current_count
            return dictionary
        else:
            time.sleep(0.1)
            current_count: int = len(os.listdir(dictionary["whole_session_data"]["dicom_dir_path"]))

def block_setup(dictionary: dict, block: int) -> Tuple[int, dict]:
    block += 1
    log_MW.print_and_log(f"Starting Block{block} ... ")

    dictionary[f"block{block}"]: dict = {}
    if "block_start_time" not in dictionary[f"block{block}"]:
        dictionary[f"block{block}"]["block_start_time"] = calculations_SH.get_time(action="get_time")

    # initialize block-specific variables
    dictionary[f"block{block}"]["num_trials_failed"]: int = 0
    dictionary[f"block{block}"]["nii_list"]: list = []
    dictionary[f"block{block}"]["event_dict"]: dict = {}
    dictionary[f"block{block}"]["resid_list"]: list = []
    dictionary[f"block{block}"]["nf_scores"]: list = []

    return block, dictionary

def trial_setup(dictionary: dict, trial: int, block: int) -> dict:
    log_SH.print_and_log("========================================")
    log_SH.print_and_log(f"Starting Block{block}, Trial {trial}... ")
    log_SH.print_and_log("========================================")

    dictionary[f"block{block}"][f"trial{trial}"]: dict = {}
    dictionary[f"block{block}"][f"trial{trial}"]["trial_start_time"] = calculations_SH.get_time(action="get_time")

    return dictionary

def end_trial(dictionary: dict, block: int, trial: int) -> dict:
    log_SH.print_and_log(f"Ending Block{block}, Trial {trial}... ")
    dictionary[f"block{block}"][f"trial{trial}"]["ending_trial_time"] = calculations_SH.get_time(action="get_time")
    dictionary[f"block{block}"][f"trial{trial}"]["total_trial_time"] = calculations_SH.get_time(
        action="subtract_times", time1=dictionary[f"block{block}"][f"trial{trial}"]["trial_start_time"])

    return dictionary

def check_to_end_block(dictionary: dict, trial: int, keyboard_stop: bool = False, ending_session: bool = False) -> Tuple[dict, bool]:
    current_block: str = dict_get_most_recent(dictionary=dictionary, get="block")
    EndBlock = False
    # End Block Due To Too Many Errors
    if dictionary[current_block]["num_trials_failed"] >= settings.RETRIES_BEFORE_ENDING:
        log_SH.print_and_log("Ending Block Due to Too Many Issues")

        if "blocks_failed" not in dictionary["whole_session_data"]:
            dictionary["whole_session_data"]["blocks_failed"]: int = 1
        else:
            dictionary["whole_session_data"]["blocks_failed"] += 1
            if dictionary["whole_session_data"]["blocks_failed"] >= settings.RETRIES_BEFORE_ENDING:
                end_session(dictionary=dictionary, reason="Too Many Errors")

        EndBlock = True

    # End Block Due to Running All Trials
    if trial == settings.NFB_N_TRIALS:
        log_SH.print_and_log("Finished Last Trial.")
        EndBlock = True

    if keyboard_stop:
        EndBlock = True
    if ending_session:
        EndBlock = True

    if EndBlock:
        dictionary[current_block]["block_end_time"] = calculations_SH.get_time(action="get_time")
        dictionary[current_block]["total_block_time"] = calculations_SH.get_time(action="subtract_times", time1=dictionary[current_block]["block_start_time"])

        file_handler.clear_nifti_dir()  # clear nifti files from the temporary dir

    return dictionary, EndBlock

def end_session(dictionary: dict, reason: str = None):
    current_block, current_trial = dict_get_most_recent(dictionary=dictionary, get="both")

    # Get the current stack frame
    stack = inspect.stack()
    if not stack[1].function == "check_to_end_block":  # If the 2nd most recent function called in the stack is check_to_end_block, don't re-run check_to_end_block
        check_to_end_block(dictionary=dictionary, ending_session=True, trial=current_trial)  # must close out block before closing session

    dictionary["whole_session_data"]["scripting_ending_time"]: datetime = calculations_SH.get_time(action="get_time")
    dictionary["whole_session_data"]["script_total_time"]: datetime = calculations_SH.get_time(action="subtract_times", time1=dictionary["whole_session_data"]["script_starting_time"])

    if reason is None:
        dictionary["whole_session_data"]["script_ending_cause"]: str = "routine or unrecorded"
    else:
        dictionary["whole_session_data"]["script_ending_cause"]: str = reason

    if reason is not None:
        log_SH.print_and_log(f"Ending Session Due to: {reason}")

    log_SH.print_and_log("Session Data:")
    # pprint.pprint(dictionary)
    csv_log_path: str = log_SH.create_log(filetype=".csv", log_name=f"{dictionary['whole_session_data']['pid']}_data_dictionary")
    log_SH.update_log(log_name=csv_log_path, dictionary_to_write=dictionary)
    dictionary["whole_session_data"]["csv_log_path"]: str = csv_log_path

    sys.exit(1)
def get_participant_id() -> str:
    acceptable_characters: list = ["p", "P", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    while True:
        Retrying: bool = False
        pid: str = input("Enter PID: ")

        if not pid.startswith("p") and not pid.startswith("P"):
            print("Please Assure Your Inputted PID starts with 'P' or 'p'")
            Retrying: bool = True

        if len(pid) == 1:
            print("Please Assure Your PID Follows Syntax: the letter 'p' followed by numbers only.")
            Retrying: bool = True

        for character in pid:
            iterator: float = 0
            if character not in acceptable_characters:
                if iterator == 0:  # only print out this line once (not for every unacceptable character)
                    print("Please Assure Your PID Follows Syntax: the letter 'p' followed by numbers only.")
                iterator += 1
                Retrying: bool = True

        if not Retrying:
            print(f"OK, Using PID: {pid}")
            break

    return pid
