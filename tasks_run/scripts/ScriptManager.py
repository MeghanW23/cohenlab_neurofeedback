import pygame
import settings
import Logger
import traceback
from datetime import datetime
from typing import Union, Tuple
import sys
import os
import time
import Calculator
import inspect
import FileHandler
import Projector
from datetime import datetime 

def retry_if_error(dictionary: dict):
    def decorator(func):
        def wrapper(*args, **kwargs):
            num_retries: int = settings.RETRIES_BEFORE_ENDING
            retries_left: int = num_retries
            current_block, current_trial = dict_get_most_recent(dictionary=dictionary, get="both")

            while retries_left >= 0:
                try:
                    if "this_trial_tries" not in dictionary[current_block][current_trial]:
                        dictionary[current_block][current_trial]["this_trial_tries"] = 1
                    else:
                        dictionary[current_block][current_trial]["this_trial_tries"] += 1

                    updated_dictionary = func(*args, **kwargs)

                    Logger.print_and_log("Inter-Trial Calculations Successful.")
                    dictionary[current_block][current_trial]["successful_trial_end"] = True
                    return updated_dictionary  # Return the result if successful

                except Exception as e:
                    # Print Error To User and Terminal Printout Log
                    Logger.print_and_log("Error:")
                    Logger.print_and_log(e)
                    traceback_str = traceback.format_exc()
                    Logger.print_and_log(traceback_str)

                    # Record Time of Error
                    now: datetime = datetime.now()
                    string_time: str = now.strftime("%Y%m%d_%Hh%Mm%Ss")

                    if retries_left <= settings.TRIES_BEFORE_NEW_DCM:
                        Logger.print_and_log("Getting New Dicom Instead...")
                        wait_for_new_dicom(dictionary=dictionary)

                    # Send Error Information To Dictionary Log
                    if "errors" not in dictionary[current_block][current_trial]:
                        dictionary[current_block][current_trial]["errors"] = []

                    info_for_log: tuple[str:str] = f"time_of_error: {string_time}", traceback_str
                    dictionary[current_block][current_trial]["errors"].append(info_for_log)

                    if "num_trials_with_errors" not in dictionary[current_block]:
                        dictionary[current_block]["num_trials_with_errors"] = 1
                    else:
                        dictionary[current_block]["num_trials_with_errors"] += 1


                    if retries_left == 0:
                        Logger.print_and_log("Ran out of retries. Skipping this trial.")

                        dictionary[current_block]["num_trials_failed"] += 1

                        dictionary[current_block][current_trial]["successful_trial_end"] = False

                        return dictionary  # Return None or handle as needed

                    Logger.print_and_log(f"Retries left: {retries_left}")
                    retries_left = retries_left - 1

        return wrapper

    return decorator
def dict_get_most_recent(dictionary: dict, get: str) -> Union[str, Tuple[str, str]]:
    if get != "block" and get != "trial" and get != "both":
        Logger.print_and_log(f"Invalid option for param: 'get' in function: dict_get_most_recent")
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
    starttime = datetime.now()
    Logger.print_and_log("Waiting For New File ...")
    current_count: int = len(os.listdir(dictionary["whole_session_data"]["dicom_dir_path"]))
    last_logged_count: int = dictionary["whole_session_data"]["dicoms_in_dir"]

    while True:
        if current_count != last_logged_count:
            Logger.print_and_log("New File Found In Dir...")
            Logger.print_and_log(f"Total Wait Time: {datetime.now() - starttime}")
            dictionary["whole_session_data"]["dicoms_in_dir"] = current_count
            return dictionary
        else:
            time.sleep(0.1)
            current_count: int = len(os.listdir(dictionary["whole_session_data"]["dicom_dir_path"]))
def block_setup(dictionary: dict, block: int, screen: pygame.Surface) -> Tuple[int, dict]:
    block += 1
    Logger.print_and_log(f"Starting Block{block} ... ")

    dictionary[f"block{block}"] = {}
    if "block_start_time" not in dictionary[f"block{block}"]:
        dictionary[f"block{block}"]["block_start_time"] = Calculator.get_time(action="get_time")

    # initialize block-specific variables
    dictionary[f"block{block}"]["num_trials_failed"] = 0
    dictionary[f"block{block}"]["nii_list"] = []
    dictionary[f"block{block}"]["event_dict"] = {}
    dictionary[f"block{block}"]["resid_list"] = []
    dictionary[f"block{block}"]["nf_scores"] = []

    Projector.show_message(screen=screen, message=settings.BLOCK_START_MESSAGE, wait_for_scanner=True)

    return block, dictionary
def trial_setup(dictionary: dict, trial: int, block: int) -> dict:
    Logger.print_and_log("================================================================================")
    Logger.print_and_log(f"Starting Block{block}, Trial {trial}... ")
    Logger.print_and_log("================================================================================")

    if script_name_in_stack(settings.RIFG_SCRIPT_NAME):
        dictionary[f"trial{trial}"] = {}
        dictionary[f"trial{trial}"]["trial_start_time"] = Calculator.get_time(action="get_time")

    dictionary[f"block{block}"][f"trial{trial}"] = {}
    dictionary[f"block{block}"][f"trial{trial}"]["trial_start_time"] = Calculator.get_time(action="get_time")

    return dictionary
def end_trial(dictionary: dict, block: int, trial: int) -> dict:
    Logger.print_and_log(f"Ending Block{block}, Trial {trial}... ")
    dictionary[f"block{block}"][f"trial{trial}"]["ending_trial_time"] = Calculator.get_time(action="get_time")
    dictionary[f"block{block}"][f"trial{trial}"]["total_trial_time"] = Calculator.get_time(
        action="subtract_times", time1=dictionary[f"block{block}"][f"trial{trial}"]["trial_start_time"])

    return dictionary
def check_to_end_block(dictionary: dict, trial: int, screen: pygame.Surface, keyboard_stop: bool = False, ending_session: bool = False, block_num: int = None) -> Tuple[dict, bool]:
    current_block: str = dict_get_most_recent(dictionary=dictionary, get="block")
    EndBlock = False
    # End Block Due To Too Many Errors
    if dictionary[current_block]["num_trials_failed"] >= settings.RETRIES_BEFORE_ENDING:
        Logger.print_and_log("Ending Block Due to Too Many Issues")

        if "blocks_failed" not in dictionary["whole_session_data"]:
            dictionary["whole_session_data"]["blocks_failed"] = 1
        else:
            dictionary["whole_session_data"]["blocks_failed"] += 1
            if dictionary["whole_session_data"]["blocks_failed"] >= settings.RETRIES_BEFORE_ENDING:
                end_session(dictionary=dictionary, reason="Too Many Errors", screen=screen)

        EndBlock = True

    trial_count: int = 0
    if script_name_in_stack(settings.RIFG_SCRIPT_NAME):
        trial_count: int = settings.RIFG_N_TRIALS

    # End Block Due to Running All Trials
    if block_num is not None:
        if block_num % 2 == 0:
            trial_count: int = settings.NFB_N_TRIALS_EVEN_BLOCK
        else:
            trial_count: int = settings.NFB_N_TRIALS_ODD_BLOCK

    dictionary["whole_session_data"]["number_of_trials"] = trial_count

    if trial == trial_count:
        Logger.print_and_log("Finished Last Trial.")
        EndBlock = True

    if keyboard_stop:
        EndBlock = True
    if ending_session:
        EndBlock = True

    if EndBlock:
        dictionary[current_block]["block_end_time"] = Calculator.get_time(action="get_time")
        dictionary[current_block]["total_block_time"] = Calculator.get_time(action="subtract_times", time1=dictionary[current_block]["block_start_time"])

        FileHandler.clear_nifti_dir()  # clear nifti files from the temporary dir

    return dictionary, EndBlock
def end_session(dictionary: dict,  screen: pygame.Surface, reason: str = None,):
    current_block, current_trial = dict_get_most_recent(dictionary=dictionary, get="both")

    # Get the current stack frame
    stack = inspect.stack()
    if not stack[1].function == "check_to_end_block":  # If the 2nd most recent function called in the stack is check_to_end_block, don't re-run check_to_end_block
        check_to_end_block(dictionary=dictionary, ending_session=True, trial=current_trial, screen=screen)  # must close out block before closing session

    dictionary["whole_session_data"]["scripting_ending_time"] = Calculator.get_time(action="get_time")
    dictionary["whole_session_data"]["script_total_time"] = Calculator.get_time(action="subtract_times", time1=dictionary["whole_session_data"]["script_starting_time"])

    if reason is None:
        dictionary["whole_session_data"]["script_ending_cause"] = "routine or unrecorded"
    else:
        dictionary["whole_session_data"]["script_ending_cause"] = reason

    if reason is not None:
        Logger.print_and_log(f"Ending Session Due to: {reason}")

    # Logger.print_and_log("Session Data:")
    # pprint.pprint(dictionary)
    csv_log_path: str = Logger.create_log(filetype=".csv", log_name=f"{dictionary['whole_session_data']['pid']}_data_dictionary")
    Logger.update_log(log_name=csv_log_path, dictionary_to_write=dictionary)
    dictionary["whole_session_data"]["csv_log_path"] = csv_log_path

    Projector.show_end_message(screen=screen, dictionary=dictionary)

    sys.exit(1)
def get_participant_id() -> str:
    acceptable_characters: list = ["p", "P", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    while True:
        Retrying: bool = False
        pid: str = input("Enter PID: ")
        pid = pid.replace("s", "") # scanner impulse presses 's' on computer 

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
def script_name_in_stack(script_name: str) -> bool:
    # Get the current stack frames
    frames = inspect.stack()

    # Iterate over each frame in the stack
    for frame in frames:
        # Get the filename (script name) for the current frame
        if script_name in frame.filename:
            return True

    return False
def start_session(dictionary: dict) -> dict:
    if script_name_in_stack(settings.NFB_SCRIPT_NAME):
        dictionary["whole_session_data"]["pid"] = get_participant_id()
        dictionary["whole_session_data"]["script_starting_time"] = Calculator.get_time(action="get_time")

        text_log_path: str = Logger.create_log(timestamp=dictionary["whole_session_data"]["script_starting_time"].strftime("%Y%m%d_%Hh%Mm%Ss"),
                                               filetype=".txt",
                                               log_name=f"{dictionary['whole_session_data']['pid']}_calculator_script")
        dictionary["whole_session_data"]["output_text_logfile_path"] = text_log_path

        dictionary["whole_session_data"]["sambashare_dir_path"] = settings.SAMBASHARE_DIR_PATH
        dictionary["whole_session_data"]["starting_block"] = settings.STARTING_BLOCK_NUM
        dictionary["whole_session_data"]["retries_before_ending"] = settings.RETRIES_BEFORE_ENDING
        dictionary["whole_session_data"]["roi_mask_dir_path"] = settings.ROI_MASK_DIR_PATH
        roi_mask_path: str = FileHandler.get_most_recent(action="roi_mask")
        dictionary["whole_session_data"]["roi_mask_path"] = roi_mask_path

        dictionary["whole_session_data"]["log_directory_path"] = settings.NFB_LOG_DIR

        dictionary["whole_session_data"]["dicom_dir_path"] = FileHandler.get_most_recent(action="dicom_dir")
        Logger.print_and_log(f"dicom dir using: {dictionary['whole_session_data']['dicom_dir_path']}")
        dictionary["whole_session_data"]["starting_dicoms_in_dir"] = len(os.listdir(dictionary["whole_session_data"]["dicom_dir_path"]))  # record initial count
        dictionary["whole_session_data"]["dicoms_in_dir"] = len(os.listdir(dictionary["whole_session_data"]["dicom_dir_path"]))  # initialize the dicoms_in_dir var

        return dictionary

    elif script_name_in_stack(settings.RIFG_SCRIPT_NAME):
        dictionary["whole_session_data"]["pid"] = get_participant_id()
        dictionary["whole_session_data"]["output_log_dir"] = Logger.create_log(filetype=".txt", log_name=f"{dictionary['whole_session_data']['pid']}_rifg_task")

        dictionary["whole_session_data"]["script_starting_time"] = Calculator.get_time(action="get_time")
        dictionary["whole_session_data"]["sambashare_dir_path"] = settings.SAMBASHARE_DIR_PATH
        dictionary["whole_session_data"]["starting_block"] = settings.STARTING_BLOCK_NUM
        dictionary["whole_session_data"]["retries_before_ending"] = settings.RETRIES_BEFORE_ENDING

        dictionary["whole_session_data"]["n_trials"] = settings.RIFG_N_TRIALS
        dictionary["whole_session_data"]["ISI_min"] = settings.ISI_MIN
        dictionary["whole_session_data"]["ISI_max"] = settings.ISI_MAX
        dictionary["whole_session_data"]["ISI_step"] = settings.ISI_STEP

        return dictionary

    else:
        print("No code made for the task/main script calling ScriptManager.start_session()")
        sys.exit(1)
def check_dicom_rerun(dictionary: dict, block: int, trial: int) -> dict:
    # if there is already a dicom path recorded for this trial, it indicated this trial is being re-run, so add the older dicom to failed dicoms
    if "dicom_path" in dictionary[f"block{block}"][f"trial{trial}"]:
        if "failed_dicoms" not in dictionary[f"block{block}"][f"trial{trial}"]:
            dictionary[f"block{block}"][f"trial{trial}"]["failed_dicoms"] = [
                dictionary[f"block{block}"][f"trial{trial}"]["dicom_path"]]
        elif dictionary[f"block{block}"][f"trial{trial}"]["dicom_path"] not in \
                dictionary[f"block{block}"][f"trial{trial}"]["failed_dicoms"]:
            dictionary[f"block{block}"][f"trial{trial}"]["failed_dicoms"].append(
                dictionary[f"block{block}"][f"trial{trial}"]["dicom_path"])

    return dictionary
def keyboard_stop(dictionary: dict, trial: int, screen: pygame.Surface, block: int = None):

    if f"trial{trial}" in dictionary[f"block{block}"]:
        dictionary[f"block{block}"][f"trial{trial}"]["keyboard_interrupt"] = Calculator.get_time(action="get_time")

    elif f"block{block}" in dictionary:
        dictionary[f"block{block}"]["keyboard_interrupt"] = Calculator.get_time(
            action="get_time")

    Logger.print_and_log("What Would You Like to Do?")
    Logger.print_and_log("(1) Continue With The Block")
    Logger.print_and_log("(2) End The Session")
    Logger.print_and_log("(3) Start New Block")

    DoingNextSteps: bool = True
    EndBlock: bool = False
    while DoingNextSteps:
        next_steps: str = input("Enter 1, 2, or 3: ")
        if next_steps != '1' and next_steps != '2' and next_steps != '3':
            Logger.print_and_log("Not a Valid Input, Please Try Again.")

        elif next_steps == '1':
            Logger.print_and_log("Ok, Let's Continue ...")
            break

        elif next_steps == '2':
            Logger.print_and_log("Ok, Let's End the Session...")

            end_session(dictionary=dictionary, reason="keyboard interrupt", screen=screen)

        elif next_steps == '3':
            Logger.print_and_log("Ok, Starting New Block...")
            Data_Dictionary, EndBlock = check_to_end_block(dictionary=dictionary, trial=trial, keyboard_stop=True, screen=screen)
            DoingNextSteps = False

    return dictionary, EndBlock