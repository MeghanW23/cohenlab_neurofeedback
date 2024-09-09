import time
import file_handler
import calculations
import log
import settings
import pprint
import sys
from typing import Union, Tuple
from datetime import datetime
import traceback
import inspect


Data_Dictionary: dict = {'whole_session_data': {}}

""" FUNCTIONS """
def retry_if_error(dictionary: dict):
    def decorator(func):
        def wrapper(*args, **kwargs):
            num_retries = settings.RETRIES_BEFORE_ENDING
            retries_left = num_retries
            current_block, current_trial = dict_get_most_recent(dictionary=dictionary, get="both")

            while retries_left > 0:
                try:
                    updated_dictionary = func(*args, **kwargs)

                    dictionary[current_block][current_trial]["successful_trial_end"]: bool = True
                    return updated_dictionary  # Return the result if successful

                except Exception as e:
                    # Print Error To User and Terminal Printout Log
                    log.print_and_log("Error:")
                    log.print_and_log(e)
                    traceback_str = traceback.format_exc()
                    log.print_and_log(traceback_str)

                    # Record Time of Error
                    now: datetime = datetime.now()
                    string_time: str = now.strftime("%Y%m%d_%Hh%Mm%Ss")

                    # Send Error Information To Dictionary Log
                    if "errors" not in dictionary[current_block][current_trial]:
                        dictionary[current_block][current_trial]["errors"]: list = []

                    info_for_log: tuple[str:str] = f"time_of_error: {string_time}", traceback_str
                    dictionary[current_block][current_trial]["errors"].append(info_for_log)

                    retries_left -= 1
                    log.print_and_log(f"Retries left: {retries_left}")

                    if "this_trial_retries" not in dictionary[current_block][current_trial]:
                        dictionary[current_block][current_trial]["this_trial_retries"]: int = 1
                    else:
                        dictionary[current_block][current_trial]["this_trial_retries"] += 1

                    if retries_left <= 0:
                        log.print_and_log("Ran out of retries. Skipping this trial.")

                        dictionary[f"block{block}"]["num_trials_failed"] += 1

                        dictionary[current_block][current_trial]["successful_trial_end"]: bool = False

                        return dictionary  # Return None or handle as needed

        return wrapper

    return decorator

@retry_if_error(dictionary=Data_Dictionary)
def run_trial(trial: int, block: int, dictionary: dict) -> dict:
    dicom_path: str = file_handler.get_most_recent(action="dicom", dicom_dir=Data_Dictionary["whole_session_data"]["dicom_dir_path"])
    print(f"Using DICOM:{dicom_path}")

    dictionary[f"block{block}"][f"trial{trial}"]["dicom_path"]: str = dicom_path

    file_handler.dicom_to_nifti(dicom_file=dicom_path, trial=trial)

    if trial % 3 == 0:
        raise Exception

    calculations.get_mean_activation()

    calculations.get_resid()

    return dictionary

def block_setup(dictionary: dict, block: int) -> Tuple[int, dict]:
    block += 1
    log.print_and_log(f"Starting Block{block} ... ")

    dictionary[f"block{block}"]: dict = {}
    if "block_start_time" not in dictionary[f"block{block}"]:
        dictionary[f"block{block}"]["block_start_time"] = calculations.get_time(action="get_time")

    dictionary[f"block{block}"]["num_trials_failed"]: int = 0

    return block, dictionary

def trial_setup(dictionary: dict, trial: int) -> dict:
    log.print_and_log("========================================")
    log.print_and_log(f"Starting Block{block}, Trial {trial}... ")
    log.print_and_log("========================================")

    dictionary[f"block{block}"][f"trial{trial}"]: dict = {}
    dictionary[f"block{block}"][f"trial{trial}"]["trial_start_time"] = calculations.get_time(action="get_time")

    return dictionary

def end_trial(dictionary: dict, block: int, trial: int) -> dict:
    log.print_and_log(f"Ending Block{block}, Trial {trial}... ")
    dictionary[f"block{block}"][f"trial{trial}"]["ending_trial_time"] = calculations.get_time(action="get_time")
    dictionary[f"block{block}"][f"trial{trial}"]["total_trial_time"] = calculations.get_time(
        action="subtract_times", time1=dictionary[f"block{block}"][f"trial{trial}"]["trial_start_time"])

    return dictionary

def check_to_end_block(dictionary: dict, keyboard_stop: bool = False, ending_session: bool = False) -> Tuple[dict, bool]:
    current_block: str = dict_get_most_recent(dictionary=dictionary, get="block")
    EndBlock = False
    # End Block Due To Too Many Errors
    if dictionary[current_block]["num_trials_failed"] >= settings.RETRIES_BEFORE_ENDING:
        log.print_and_log("Ending Block Due to Too Many Issues")

        if "blocks_failed" not in dictionary["whole_session_data"]:
            dictionary["whole_session_data"]["blocks_failed"]: int = 1
        else:
            dictionary["whole_session_data"]["blocks_failed"] += 1
            if dictionary["whole_session_data"]["blocks_failed"] >= settings.RETRIES_BEFORE_ENDING:
                end_session(dictionary=dictionary, reason="Too Many Errors")

        EndBlock = True

    # End Block Due to Running All Trials
    if trial == settings.NFB_N_TRIALS:
        log.print_and_log("Finished Last Trial.")
        EndBlock = True

    if keyboard_stop:
        EndBlock = True
    if ending_session:
        EndBlock = True

    if EndBlock:
        dictionary[current_block]["block_end_time"] = calculations.get_time(action="get_time")
        dictionary[current_block]["total_block_time"] = calculations.get_time(action="subtract_times", time1=dictionary[current_block]["block_start_time"])

        file_handler.clear_nifti_dir() # clear nifti files from the temporary dir

    return dictionary, EndBlock

def end_session(dictionary: dict, reason: str = None):
    # Get the current stack frame
    stack = inspect.stack()
    if not stack[1].function == "check_to_end_block":  # If the 2nd most recent function called in the stack is check_to_end_block, don't re-run check_to_end_block
        check_to_end_block(dictionary=dictionary, ending_session=True)  # must close out block before closing session

    dictionary["whole_session_data"]["scripting_ending_time"]: datetime = calculations.get_time(action="get_time")
    dictionary["whole_session_data"]["script_total_time"]: datetime = calculations.get_time(action="subtract_times", time1=
    dictionary["whole_session_data"]["script_starting_time"])

    if reason is None:
        dictionary["whole_session_data"]["script_ending_cause"]: str = "routine or unrecorded"
    else:
        dictionary["whole_session_data"]["script_ending_cause"]: str = reason

    if reason is not None:
        log.print_and_log(f"Ending Session Due to: {reason}")

    log.print_and_log("Session Data:")
    pprint.pprint(Data_Dictionary)

    string_end_time: str = dictionary["whole_session_data"]["scripting_ending_time"].strftime("%Y%m%d_%Hh%Mm%Ss")

    sys.exit(1)

def dict_get_most_recent(dictionary: dict, get: str) -> Union[str, Tuple[str, str]]:

    if get != "block" and get != "trial" and get != "both":
        log.print_and_log(f"Invalid option for param: 'get' in function: dict_get_most_recent")
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

""" SESSION SETUP """
log.print_and_log("Running Main Calculation Script ... ")
Data_Dictionary["whole_session_data"]["script_starting_time"]: datetime = calculations.get_time(action="get_time")
Data_Dictionary["whole_session_data"]["sambashare_dir_path"]: str = settings.SAMBASHARE_DIR_PATH
Data_Dictionary["whole_session_data"]["roi_mask_dir_path"]: str = settings.ROI_MASK_DIR_PATH
Data_Dictionary["whole_session_data"]["log_directory_path"]: str = settings.LOGGING_DIR_PATH
Data_Dictionary["whole_session_data"]["starting_block"]: int = settings.STARTING_BLOCK_NUM
Data_Dictionary["whole_session_data"]["starting_block"]: int = settings.STARTING_BLOCK_NUM
Data_Dictionary["whole_session_data"]["number_of_trials"]: int = settings.NFB_N_TRIALS
Data_Dictionary["whole_session_data"]["retries_before_ending"]: int = settings.RETRIES_BEFORE_ENDING

# In Order to Log Things Happening in Other Scripts, We must create the log before calling any other scripts
text_log_path: str = log.create_log(
    timestamp=Data_Dictionary["whole_session_data"]["script_starting_time"].strftime("%Y%m%d_%Hh%Mm%Ss"),
    filetype=".txt",
    log_name="calculator_script")

Data_Dictionary["whole_session_data"]["output_text_logfile_path"]: str = text_log_path

roi_mask_path: str = file_handler.get_most_recent(action="roi_mask")
Data_Dictionary["whole_session_data"]["roi_mask_path"]: str = roi_mask_path

dicom_dir_path: str = file_handler.get_most_recent(action="dicom_dir")
Data_Dictionary["whole_session_data"]["dicom_dir_path"]: str = dicom_dir_path


starting_block_num: int = settings.STARTING_BLOCK_NUM
block: int = starting_block_num - 1

RunningBlock: bool = True
while RunningBlock:
    block, Data_Dictionary = block_setup(dictionary=Data_Dictionary, block=block)  # Block Setup Func

    for trial in range(1, settings.NFB_N_TRIALS + 1):
        try:

            # Trial Setup
            Data_Dictionary = trial_setup(dictionary=Data_Dictionary, trial=trial)

            time.sleep(1)

            # Run Trial
            run_trial(trial=trial, block=block, dictionary=Data_Dictionary)

            # End Trial
            Data_Dictionary = end_trial(dictionary=Data_Dictionary, block=block, trial=trial)

            # Check if Block Should End
            Data_Dictionary, EndBlock = check_to_end_block(dictionary=Data_Dictionary)
            if EndBlock:
                break  # break current for loop, start new block

        except KeyboardInterrupt as e:
            Data_Dictionary[f"block{block}"][f"trial{trial}"]["keyboard_interrupt"]: bool = calculations.get_time(action="get_time")
            log.print_and_log("---- Keyboard Interrupt Detected ----")
            log.print_and_log("What Would You Like to Do?")
            log.print_and_log("(1) Continue With The Block")
            log.print_and_log("(2) End The Session")
            log.print_and_log("(3) Start New Block")

            DoingNextSteps: bool = True
            EndBlock: bool = False
            while DoingNextSteps:
                next_steps: str = input("Enter 1, 2, or 3: ")
                if next_steps != '1' and next_steps != '2' and next_steps != '3':
                    log.print_and_log("Not a Valid Input, Please Try Again.")

                elif next_steps == '1':
                    log.print_and_log("Ok, Let's Continue ...")
                    break

                elif next_steps == '2':
                    log.print_and_log("Ok, Let's End the Session...")

                    end_session(dictionary=Data_Dictionary, reason="keyboard interrupt")

                elif next_steps == '3':
                    log.print_and_log("Ok, Starting New Block...")
                    Data_Dictionary, EndBlock = check_to_end_block(dictionary=Data_Dictionary, keyboard_stop=True)
                    DoingNextSteps = False

            if EndBlock:
                break  # break current for loop, start new block

# End Script
end_session(dictionary=Data_Dictionary)

