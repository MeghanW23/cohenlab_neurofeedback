import os
import file_handler
import calculations_MW
import log_MW
import settings
from datetime import datetime
import script_manager

Data_Dictionary: dict = {'whole_session_data': {}}
""" FUNCTIONS """
@script_manager.retry_if_error(dictionary=Data_Dictionary)
def run_trial(trial: int, block: int, dictionary: dict) -> dict:
    script_manager.check_dicom_rerun(dictionary=dictionary, block=block, trial=trial)

    dictionary[f"block{block}"][f"trial{trial}"]["dicom_path"]: str = file_handler.get_most_recent(action="dicom", dicom_dir=Data_Dictionary["whole_session_data"]["dicom_dir_path"])
    log_MW.print_and_log(f"Using DICOM:{dictionary[f'block{block}'][f'trial{trial}']['dicom_path']}")

    if dictionary[f"block{block}"][f"trial{trial}"]["this_trial_tries"] > 1:
        WaitAfterRun: bool = True
    else:
        WaitAfterRun: bool = False

    dictionary[f"block{block}"][f"trial{trial}"]["nifti_path"] = file_handler.dicom_to_nifti(dicom_file=dictionary[f"block{block}"][f"trial{trial}"]["dicom_path"], trial=trial, WaitAfterRun=WaitAfterRun)

    dictionary[f"block{block}"][f"trial{trial}"]["mean_activation"] = calculations_MW.get_mean_activation(roi_mask=dictionary["whole_session_data"]["roi_mask_path"], nifti_image_path=dictionary[f"block{block}"][f"trial{trial}"]["nifti_path"])

    return dictionary

""" SESSION SETUP """
Data_Dictionary: dict = script_manager.start_session(dictionary=Data_Dictionary)
starting_block_num: int = settings.STARTING_BLOCK_NUM
block: int = starting_block_num - 1

log_MW.print_and_log("Running Main Calculation Script ... ")
RunningBlock: bool = True
while RunningBlock:
    block, Data_Dictionary = script_manager.block_setup(dictionary=Data_Dictionary, block=block)  # Block Setup Func

    for trial in range(1, settings.NFB_N_TRIALS + 1):
        try:
            # Trial Setup
            Data_Dictionary = script_manager.trial_setup(dictionary=Data_Dictionary, trial=trial, block=block)

            # Wait for New Dicom
            Data_Dictionary = script_manager.wait_for_new_dicom(dictionary=Data_Dictionary)

            # Run Trial
            run_trial(trial=trial, block=block, dictionary=Data_Dictionary)

            # End Trial
            Data_Dictionary = script_manager.end_trial(dictionary=Data_Dictionary, block=block, trial=trial)

            # Check if Block Should End
            Data_Dictionary, EndBlock = script_manager.check_to_end_block(dictionary=Data_Dictionary, trial=trial)
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

                    script_manager.end_session(dictionary=Data_Dictionary, reason="keyboard interrupt")

                elif next_steps == '3':
                    log_MW.print_and_log("Ok, Starting New Block...")
                    Data_Dictionary, EndBlock = script_manager.check_to_end_block(dictionary=Data_Dictionary, trial=trial, keyboard_stop=True)
                    DoingNextSteps = False

            if EndBlock:
                break  # break current for loop, start new block

# End Script
script_manager.end_session(dictionary=Data_Dictionary)
