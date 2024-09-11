import os
import time
import file_handler
import calculations_MW
import log_MW
import settings
import pprint
import sys
from typing import Union, Tuple, Type
from datetime import datetime
import traceback
import inspect


Data_Dictionary: dict = {'whole_session_data': {}}

""" FUNCTIONS """
def retry_if_error(dictionary: dict):
    def decorator(func):
        def wrapper(*args, **kwargs):
            num_retries: int = settings.RETRIES_BEFORE_ENDING
            retries_left: int = num_retries
            current_block, current_trial = dict_get_most_recent(dictionary=dictionary, get="both")

            while retries_left >= 0:
                try:
                    updated_dictionary = func(*args, **kwargs)

                    dictionary[current_block][current_trial]["successful_trial_end"]: bool = True
                    print("no error in dcm2niix")
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

                    if retries_left == 1:
                        log_MW.print_and_log("Getting New Dicom Instead")
                        wait_for_new_dicom(dictionary=dictionary)

                    # Send Error Information To Dictionary Log
                    if "errors" not in dictionary[current_block][current_trial]:
                        dictionary[current_block][current_trial]["errors"]: list = []

                    info_for_log: tuple[str:str] = f"time_of_error: {string_time}", traceback_str
                    dictionary[current_block][current_trial]["errors"].append(info_for_log)

                    log_MW.print_and_log(f"Retries left: {retries_left}")
                    """
                    if retries_left == 3:
                        log_MW.print_and_log(f"retrying after: {settings.RETRY_WAIT_TIMES[0]}s")
                        time.sleep(settings.RETRY_WAIT_TIMES[0])
                    elif retries_left == 2:
                        log_MW.print_and_log(f"retrying after: {settings.RETRY_WAIT_TIMES[1]}s")
                        time.sleep(settings.RETRY_WAIT_TIMES[1])
                    else:
                        log_MW.print_and_log(f"retrying after: {settings.RETRY_WAIT_TIMES[2]}s")
                        time.sleep(settings.RETRY_WAIT_TIMES[2])
                    """
                    if "this_trial_tries" not in dictionary[current_block][current_trial]:
                        dictionary[current_block][current_trial]["this_trial_tries"]: int = 1
                    else:
                        dictionary[current_block][current_trial]["this_trial_tries"] += 1

                    if retries_left == 0:
                        log_MW.print_and_log("Ran out of retries. Skipping this trial.")

                        dictionary[f"block{block}"]["num_trials_failed"] += 1

                        dictionary[current_block][current_trial]["successful_trial_end"]: bool = False

                        return dictionary  # Return None or handle as needed

                    retries_left = retries_left - 1

        return wrapper

    return decorator

@retry_if_error(dictionary=Data_Dictionary)
def run_trial(trial: int, block: int, dictionary: dict) -> dict:
    dicom_path: str = file_handler.get_most_recent(action="dicom", dicom_dir=Data_Dictionary["whole_session_data"]["dicom_dir_path"])
    log_MW.print_and_log(f"Using DICOM:{dicom_path}")

    dictionary[f"block{block}"][f"trial{trial}"]["dicom_path"]: str = dicom_path

    dictionary[f"block{block}"][f"trial{trial}"]["nifti_path"] = file_handler.dicom_to_nifti(dicom_file=dicom_path, trial=trial)

    mean_activation = calculations_MW.get_mean_activation(roi_mask=dictionary["whole_session_data"]["roi_mask_path"], nifti_image_path=dictionary[f"block{block}"][f"trial{trial}"]["nifti_path"])
    dictionary[f"block{block}"][f"trial{trial}"]["mean_activation"]: float = mean_activation
    # dictionary = calculations_MW.get_resid(dictionary=dictionary, block=block, trial=trial)

    return dictionary

def block_setup(dictionary: dict, block: int) -> Tuple[int, dict]:
    block += 1
    log_MW.print_and_log(f"Starting Block{block} ... ")

    dictionary[f"block{block}"]: dict = {}
    if "block_start_time" not in dictionary[f"block{block}"]:
        dictionary[f"block{block}"]["block_start_time"] = calculations_MW.get_time(action="get_time")

    # initialize block-specific variables
    dictionary[f"block{block}"]["num_trials_failed"]: int = 0
    dictionary[f"block{block}"]["nii_list"]: list = []
    dictionary[f"block{block}"]["event_dict"]: dict = {}
    dictionary[f"block{block}"]["resid_list"]:list = []
    dictionary[f"block{block}"]["nf_scores"]:list = []

    return block, dictionary

def trial_setup(dictionary: dict, trial: int) -> dict:
    log_MW.print_and_log("========================================")
    log_MW.print_and_log(f"Starting Block{block}, Trial {trial}... ")
    log_MW.print_and_log("========================================")

    dictionary[f"block{block}"][f"trial{trial}"]: dict = {}
    dictionary[f"block{block}"][f"trial{trial}"]["trial_start_time"] = calculations_MW.get_time(action="get_time")

    return dictionary

def end_trial(dictionary: dict, block: int, trial: int) -> dict:
    log_MW.print_and_log(f"Ending Block{block}, Trial {trial}... ")
    dictionary[f"block{block}"][f"trial{trial}"]["ending_trial_time"] = calculations_MW.get_time(action="get_time")
    dictionary[f"block{block}"][f"trial{trial}"]["total_trial_time"] = calculations_MW.get_time(
        action="subtract_times", time1=dictionary[f"block{block}"][f"trial{trial}"]["trial_start_time"])

    return dictionary

def check_to_end_block(dictionary: dict, keyboard_stop: bool = False, ending_session: bool = False) -> Tuple[dict, bool]:
    current_block: str = dict_get_most_recent(dictionary=dictionary, get="block")
    EndBlock = False
    # End Block Due To Too Many Errors
    if dictionary[current_block]["num_trials_failed"] >= settings.RETRIES_BEFORE_ENDING:
        log_MW.print_and_log("Ending Block Due to Too Many Issues")

        if "blocks_failed" not in dictionary["whole_session_data"]:
            dictionary["whole_session_data"]["blocks_failed"]: int = 1
        else:
            dictionary["whole_session_data"]["blocks_failed"] += 1
            if dictionary["whole_session_data"]["blocks_failed"] >= settings.RETRIES_BEFORE_ENDING:
                end_session(dictionary=dictionary, reason="Too Many Errors")

        EndBlock = True

    # End Block Due to Running All Trials
    if trial == settings.NFB_N_TRIALS:
        log_MW.print_and_log("Finished Last Trial.")
        EndBlock = True

    if keyboard_stop:
        EndBlock = True
    if ending_session:
        EndBlock = True

    if EndBlock:
        dictionary[current_block]["block_end_time"] = calculations_MW.get_time(action="get_time")
        dictionary[current_block]["total_block_time"] = calculations_MW.get_time(action="subtract_times", time1=dictionary[current_block]["block_start_time"])

        file_handler.clear_nifti_dir() # clear nifti files from the temporary dir

    return dictionary, EndBlock

def end_session(dictionary: dict, reason: str = None):
    # Get the current stack frame
    stack = inspect.stack()
    if not stack[1].function == "check_to_end_block":  # If the 2nd most recent function called in the stack is check_to_end_block, don't re-run check_to_end_block
        check_to_end_block(dictionary=dictionary, ending_session=True)  # must close out block before closing session

    dictionary["whole_session_data"]["scripting_ending_time"]: datetime = calculations_MW.get_time(action="get_time")
    dictionary["whole_session_data"]["script_total_time"]: datetime = calculations_MW.get_time(action="subtract_times", time1=
    dictionary["whole_session_data"]["script_starting_time"])

    if reason is None:
        dictionary["whole_session_data"]["script_ending_cause"]: str = "routine or unrecorded"
    else:
        dictionary["whole_session_data"]["script_ending_cause"]: str = reason

    if reason is not None:
        log_MW.print_and_log(f"Ending Session Due to: {reason}")

    log_MW.print_and_log("Session Data:")
    pprint.pprint(Data_Dictionary)
    csv_log_path: str = log_MW.create_log(filetype=".csv", log_name="data_dictionary")
    log_MW.update_log(log_name=csv_log_path, dictionary_to_write=Data_Dictionary)
    dictionary["whole_session_data"]["csv_log_path"]: str = csv_log_path

    sys.exit(1)

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
    last_logged_count: int = Data_Dictionary["whole_session_data"]["dicoms_in_dir"]

    while True:
        if current_count != last_logged_count:
            log_MW.print_and_log("New File Found In Dir...")
            Data_Dictionary["whole_session_data"]["dicoms_in_dir"]: int = current_count
            return dictionary
        else:
            time.sleep(0.1)
            current_count: int = len(os.listdir(dictionary["whole_session_data"]["dicom_dir_path"]))

""" SESSION SETUP """
log_MW.print_and_log("Running Main Calculation Script ... ")
Data_Dictionary["whole_session_data"]["script_starting_time"]: datetime = calculations_MW.get_time(action="get_time")
Data_Dictionary["whole_session_data"]["sambashare_dir_path"]: str = settings.SAMBASHARE_DIR_PATH
Data_Dictionary["whole_session_data"]["roi_mask_dir_path"]: str = settings.ROI_MASK_DIR_PATH
Data_Dictionary["whole_session_data"]["log_directory_path"]: str = settings.LOGGING_DIR_PATH
Data_Dictionary["whole_session_data"]["starting_block"]: int = settings.STARTING_BLOCK_NUM
Data_Dictionary["whole_session_data"]["starting_block"]: int = settings.STARTING_BLOCK_NUM
Data_Dictionary["whole_session_data"]["number_of_trials"]: int = settings.NFB_N_TRIALS
Data_Dictionary["whole_session_data"]["retries_before_ending"]: int = settings.RETRIES_BEFORE_ENDING

# In Order to Log Things Happening in Other Scripts, We must create the log before calling any other scripts
text_log_path: str = log_MW.create_log(
    timestamp=Data_Dictionary["whole_session_data"]["script_starting_time"].strftime("%Y%m%d_%Hh%Mm%Ss"),
    filetype=".txt",
    log_name="calculator_script")

Data_Dictionary["whole_session_data"]["output_text_logfile_path"]: str = text_log_path

roi_mask_path: str = file_handler.get_most_recent(action="roi_mask")
Data_Dictionary["whole_session_data"]["roi_mask_path"]: str = roi_mask_path
Data_Dictionary["whole_session_data"]["dicom_dir_path"]: str = file_handler.get_most_recent(action="dicom_dir")
log_MW.print_and_log(f"dicom dir using: {Data_Dictionary['whole_session_data']['dicom_dir_path']}")
Data_Dictionary["whole_session_data"]["starting_dicoms_in_dir"]: int = len(os.listdir(Data_Dictionary["whole_session_data"]["dicom_dir_path"])) # record initial count
Data_Dictionary["whole_session_data"]["dicoms_in_dir"]: int = len(os.listdir(Data_Dictionary["whole_session_data"]["dicom_dir_path"])) # initialize the dicoms_in_dir var


starting_block_num: int = settings.STARTING_BLOCK_NUM
block: int = starting_block_num - 1

RunningBlock: bool = True
while RunningBlock:
    block, Data_Dictionary = block_setup(dictionary=Data_Dictionary, block=block)  # Block Setup Func

    for trial in range(1, settings.NFB_N_TRIALS + 1):
        try:
            # Trial Setup
            Data_Dictionary = trial_setup(dictionary=Data_Dictionary, trial=trial)

            # Wait for New Dicom
            Data_Dictionary = wait_for_new_dicom(dictionary=Data_Dictionary)

            # Run Trial
            run_trial(trial=trial, block=block, dictionary=Data_Dictionary)

            # End Trial
            Data_Dictionary = end_trial(dictionary=Data_Dictionary, block=block, trial=trial)

            # Check if Block Should End
            Data_Dictionary, EndBlock = check_to_end_block(dictionary=Data_Dictionary)
            if EndBlock:
                break  # break current for loop, start new block

        except KeyboardInterrupt as e:
            Data_Dictionary[f"block{block}"][f"trial{trial}"]["keyboard_interrupt"]: bool = calculations_MW.get_time(action="get_time")
            log_MW.print_and_log("---- Keyboard Interrupt Detected ----")
            log_MW.print_and_log("What Would You Like to Do?")
            log_MW.print_and_log("(1) Continue With The Block")
            log_MW.print_and_log("(2) End The Session")
            log_MW.print_and_log("(3) Start New Block")

            DoingNextSteps: bool = True
            EndBlock: bool = False
            while DoingNextSteps:
                next_steps: str = input("Enter 1, 2, or 3: ")
                if next_steps != '1' and next_steps != '2' and next_steps != '3':
                    log_MW.print_and_log("Not a Valid Input, Please Try Again.")

                elif next_steps == '1':
                    log_MW.print_and_log("Ok, Let's Continue ...")
                    break

                elif next_steps == '2':
                    log_MW.print_and_log("Ok, Let's End the Session...")

                    end_session(dictionary=Data_Dictionary, reason="keyboard interrupt")

                elif next_steps == '3':
                    log_MW.print_and_log("Ok, Starting New Block...")
                    Data_Dictionary, EndBlock = check_to_end_block(dictionary=Data_Dictionary, keyboard_stop=True)
                    DoingNextSteps = False

            if EndBlock:
                break  # break current for loop, start new block

# End Script
end_session(dictionary=Data_Dictionary)

