import time
import file_handler
import calculations
import log
import settings
import pprint
import sys
from typing import Union, Tuple
from datetime import datetime

""" FUNCTIONS """
def retry_if_error(func):
    def wrapper(*args, **kwargs):
        num_retries: int = settings.RETRIES_BEFORE_ENDING
        retries_left: int = num_retries
        while retries_left > 0:
            try:
                result = func(*args, **kwargs)
                return result  # Return the result if successful

            except Exception as e:
                print("Error:")
                print(e)
                retries_left -= 1
                if retries_left <= 0:
                    print("Ran out of retries. Skipping this trial.")
                    Data_Dictionary[f"block{block}"]["trials_retried"] += 1
                    return Data_Dictionary  # Return None or handle as needed
    return wrapper
@retry_if_error
def run_trial(trial_num: int, block_num: int, dictionary: dict) -> dict:
    file_handler.get_most_recent(action="dicom")

    file_handler.dicom_to_nifti()

    time.sleep(0.5)

    if trial_num % 3 == 0:
        raise Exception

    time.sleep(0.5)

    calculations.get_mean_activation()

    calculations.get_resid()

    return dictionary

def block_setup(dictionary: dict, block: int) -> Tuple[int, dict]:
    block += 1
    print(f"Starting Block{block} ... ")

    dictionary[f"block{block}"]: dict = {}
    if "block_start_time" not in dictionary[f"block{block}"]:
        dictionary[f"block{block}"]["block_start_time"] = calculations.get_time(action="get_time")

    dictionary[f"block{block}"]["trials_retried"]: int = 0

    return block, dictionary

def trial_setup(dictionary: dict, trial: int) -> dict:
    print("========================================")
    print(f"Starting Block{block}, Trial {trial}... ")
    print("========================================")

    dictionary[f"block{block}"][f"trial{trial}"]: dict = {}
    dictionary[f"block{block}"][f"trial{trial}"]["trial_start_time"] = calculations.get_time(action="get_time")

    return dictionary

def end_trial(dictionary: dict, block: int, trial: int) -> dict:
    print(f"Ending Block{block}, Trial {trial}... ")
    dictionary[f"block{block}"][f"trial{trial}"]["ending_trial_time"] = calculations.get_time(action="get_time")
    dictionary[f"block{block}"][f"trial{trial}"]["total_trial_time"] = calculations.get_time(
        action="subtract_times", time1=dictionary[f"block{block}"][f"trial{trial}"]["trial_start_time"])

    return dictionary

def check_to_end_block(dictionary: dict, block: int, keyboard_stop: bool = False, ending_session: bool = False) -> Tuple[dict, bool]:
    EndBlock = False
    # End Block Due To Too Many Errors
    if dictionary[f"block{block}"]["trials_retried"] >= settings.RETRIES_BEFORE_ENDING:
        print("Ending Block Due to Too Many Issues")
        EndBlock = True

    # End Block Due to Running All Trials
    if trial == settings.NFB_N_TRIALS:
        print("Finished Last Trial.")
        EndBlock = True

    if keyboard_stop:
        EndBlock = True
    if ending_session:
        EndBlock = True

    if EndBlock:
        dictionary[f"block{block}"]["block_end_time"] = calculations.get_time(action="get_time")
        dictionary[f"block{block}"]["total_block_time"] = calculations.get_time(action="subtract_times", time1=dictionary[f"block{block}"]["block_start_time"])

    return dictionary, EndBlock

def end_session(dictionary: dict, block: int, keyboard_stop: bool = False):
    check_to_end_block(dictionary=dictionary, block=block, ending_session=True)
    dictionary["whole_session_data"]["scripting_ending_time"] = calculations.get_time(action="get_time")
    dictionary["whole_session_data"]["script_total_time"] = calculations.get_time(action="subtract_times", time1=
    dictionary["whole_session_data"]["script_starting_time"])

    if keyboard_stop:
        dictionary["whole_session_data"]["script_ending_cause"]: str = "keyboard interrupt"

    else:
        dictionary["whole_session_data"]["script_ending_cause"]: str = "routine or unrecorded"

    print("Session Data:")
    pprint.pprint(Data_Dictionary)

    sys.exit(1)

""" SESSION SETUP """
print("Running Main Calculation Script ... ")
Data_Dictionary: dict = {'whole_session_data': {}}
Data_Dictionary["whole_session_data"]["script_starting_time"]: datetime = calculations.get_time(action="get_time")
Data_Dictionary["whole_session_data"]["sambashare_dir_path"]: str = settings.SAMBASHARE_DIR_PATH
Data_Dictionary["whole_session_data"]["roi_mask_dir_path"]: str = settings.ROI_MASK_DIR_PATH
Data_Dictionary["whole_session_data"]["log_directory_path"]: str = settings.LOGGING_DIR_PATH
Data_Dictionary["whole_session_data"]["starting_block"]: int = settings.STARTING_BLOCK_NUM
Data_Dictionary["whole_session_data"]["starting_block"]: int = settings.STARTING_BLOCK_NUM
Data_Dictionary["whole_session_data"]["number_of_trials"]: int = settings.NFB_N_TRIALS
Data_Dictionary["whole_session_data"]["retries_before_ending"]: int = settings.RETRIES_BEFORE_ENDING

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

            # Run Trial
            run_trial(trial_num=trial, block_num=block, dictionary=Data_Dictionary)

            # End Trial
            Data_Dictionary = end_trial(dictionary=Data_Dictionary, block=block, trial=trial)

            # Check if Block Should End
            Data_Dictionary, EndBlock = check_to_end_block(dictionary=Data_Dictionary, block=block)
            if EndBlock:
                break  # break current for loop, start new block

        except KeyboardInterrupt as e:
            Data_Dictionary[f"block{block}"][f"trial{trial}"]["keyboard_interrupt"]: bool = calculations.get_time(action="get_time")
            print("---- Keyboard Interrupt Detected ----")
            print("What Would You Like to Do?")
            print("(1) Continue With The Block")
            print("(2) End The Session")
            print("(3) Start New Block")

            DoingNextSteps: bool = True
            EndBlock: bool = False
            while DoingNextSteps:
                next_steps: str = input("Enter 1, 2, or 3: ")
                if next_steps != '1' and next_steps != '2' and next_steps != '3':
                    print("Not a Valid Input, Please Try Again.")

                elif next_steps == '1':
                    print("Ok, Let's Continue ...")
                    break

                elif next_steps == '2':
                    print("Ok, Let's End the Session...")

                    end_session(dictionary=Data_Dictionary, keyboard_stop=True, block=block)

                elif next_steps == '3':
                    print("Ok, Starting New Block...")
                    Data_Dictionary, EndBlock = check_to_end_block(dictionary=Data_Dictionary, block=block, keyboard_stop=True)
                    DoingNextSteps = False

            if EndBlock:
                break  # break current for loop, start new block

# End Script
end_session(dictionary=Data_Dictionary, block=block)

