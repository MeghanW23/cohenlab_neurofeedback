import settings
import log_MW
import traceback
from datetime import datetime
from typing import Union, Tuple
import sys
import os
import time
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

                    log_MW.print_and_log("Inter-Trial Calculations Successful.")
                    dictionary[current_block][current_trial]["successful_trial_end"]: bool = True
                    return updated_dictionary  # Return the result if successful

                except Exception as e:
                    # Print Error To User and Terminal Printout Log
                    log_MW.print_and_log("Error:")
                    log_MW.print_and_log(e)
                    traceback_str = traceback.format_exc()
                    log_MW.print_and_log(traceback_str)

                    # Record Time of Error
                    now: datetime = datetime.now()
                    string_time: str = now.strftime("%Y%m%d_%Hh%Mm%Ss")

                    if retries_left <= settings.TRIES_BEFORE_NEW_DCM:
                        log_MW.print_and_log("Getting New Dicom Instead...")
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
                        log_MW.print_and_log("Ran out of retries. Skipping this trial.")

                        dictionary[current_block]["num_trials_failed"] += 1

                        dictionary[current_block][current_trial]["successful_trial_end"]: bool = False

                        return dictionary  # Return None or handle as needed

                    log_MW.print_and_log(f"Retries left: {retries_left}")
                    retries_left = retries_left - 1

        return wrapper

    return decorator

def dict_get_most_recent(dictionary: dict, get: str) -> Union[str, Tuple[str, str]]:

    if get != "block" and get != "trial" and get != "both":
        log_MW.print_and_log(f"Invalid option for param: 'get' in function: dict_get_most_recent")
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
    log_MW.print_and_log("Waiting For New File ...")
    current_count: int = len(os.listdir(dictionary["whole_session_data"]["dicom_dir_path"]))
    last_logged_count: int = dictionary["whole_session_data"]["dicoms_in_dir"]

    while True:
        if current_count != last_logged_count:
            log_MW.print_and_log("New File Found In Dir...")
            dictionary["whole_session_data"]["dicoms_in_dir"]: int = current_count
            return dictionary
        else:
            time.sleep(0.1)
            current_count: int = len(os.listdir(dictionary["whole_session_data"]["dicom_dir_path"]))
