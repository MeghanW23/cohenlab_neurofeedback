import time
import file_handler
import calculations
import settings
import pprint

Data_Dictionary: dict = {'whole_session_data': {}}
Data_Dictionary["whole_session_data"]["script_starting_time"] = calculations.get_time(action="get_time")
Data_Dictionary["whole_session_data"]["sambashare_dir"] = settings.SAMBASHARE_DIR_PATH
Data_Dictionary["whole_session_data"]["roi_mask_dir_path"] = settings.ROI_MASK_DIR_PATH
Data_Dictionary["whole_session_data"]["log_directory_path"] = settings.LOGGING_DIR_PATH
Data_Dictionary["whole_session_data"]["starting_block"] = settings.STARTING_BLOCK_NUM
Data_Dictionary["whole_session_data"]["starting_block"] = settings.STARTING_BLOCK_NUM
Data_Dictionary["whole_session_data"]["number_of_trials"] = settings.NFB_N_TRIALS
Data_Dictionary["whole_session_data"]["retries_before_ending"] = settings.RETRIES_BEFORE_ENDING
pprint.pprint(Data_Dictionary)

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
                    return None  # Return None or handle as needed
    return wrapper

@retry_if_error
def run_trial(trial_num: int, block_num: int, dictionary: dict):
    file_handler.get_most_recent(action="dicom")

    file_handler.dicom_to_nifti()

    time.sleep(0.5)

    if trial_num % 3 == 0:
        raise Exception
    time.sleep(0.5)

    calculations.get_mean_activation()

    calculations.get_resid()
    print("================")

def block_setup(dictionary: dict, block: int) -> tuple[int, dict]:
    block += 1
    print(f"Starting Block{block} ... ")

    dictionary[f"block{block}"]: dict = {}
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

def check_to_end_block(dictionary: dict, block: int) -> tuple[dict, bool]:
    EndBlock = False
    # End Block Due To Too Many Errors
    if dictionary[f"block{block}"]["trials_retried"] >= settings.RETRIES_BEFORE_ENDING:
        print("Ending Block Due to Too Many Issues")
        dictionary[f"block{block}"]["trials_retried"]: int = 0
        EndBlock = True

    # End Block Due to Running All Trials
    if trial == settings.NFB_N_TRIALS:
        print("Finished Last Trial.")
        EndBlock = True

    if EndBlock:
        dictionary[f"block{block}"]["block_end_time"] = calculations.get_time(action="get_time")
        dictionary[f"block{block}"]["block_ending_time"] = calculations.get_time(action="subtract_times", time1=dictionary[f"block{block}"]["block_start_time"])

    return dictionary, EndBlock

# Session Setup
print("Running Main Calculation Script ... ")
file_handler.get_most_recent(action="roi_mask")
file_handler.get_most_recent(action="dicom_dir")

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
            print("---- Keyboard Interrupt Detected ----")
            

        pprint.pprint(Data_Dictionary[f"block{block}"][f"trial{trial}"])


# End Script
Data_Dictionary["whole_session_data"]["script_ending_time"] = calculations.get_time(action="subtract_times", time1=Data_Dictionary["whole_session_data"]["script_starting_time"])


