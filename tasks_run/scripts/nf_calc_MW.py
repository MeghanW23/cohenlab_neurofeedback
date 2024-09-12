import FileHandler
import Calculator
import Logger
import Settings
import ScriptManager
import Projector
import pygame

Data_Dictionary: dict = {'whole_session_data': {}}
""" FUNCTIONS """
@ScriptManager.retry_if_error(dictionary=Data_Dictionary)
def run_trial(trial: int, block: int, dictionary: dict) -> dict:
    ScriptManager.check_dicom_rerun(dictionary=dictionary, block=block, trial=trial)

    dictionary[f"block{block}"][f"trial{trial}"]["dicom_path"]: str = FileHandler.get_most_recent(action="dicom", dicom_dir=Data_Dictionary["whole_session_data"]["dicom_dir_path"])
    Logger.print_and_log(f"Using DICOM:{dictionary[f'block{block}'][f'trial{trial}']['dicom_path']}")

    if dictionary[f"block{block}"][f"trial{trial}"]["this_trial_tries"] > 1:
        WaitAfterRun: bool = True
    else:
        WaitAfterRun: bool = False

    dictionary[f"block{block}"][f"trial{trial}"]["nifti_path"] = FileHandler.dicom_to_nifti(dicom_file=dictionary[f"block{block}"][f"trial{trial}"]["dicom_path"], trial=trial, WaitAfterRun=WaitAfterRun)

    dictionary[f"block{block}"][f"trial{trial}"]["mean_activation"] = Calculator.get_mean_activation(roi_mask=dictionary["whole_session_data"]["roi_mask_path"], nifti_image_path=dictionary[f"block{block}"][f"trial{trial}"]["nifti_path"])
    dictionary = Calculator.get_resid(dictionary=dictionary, block=block, trial=trial)

    if "nf_score" in Data_Dictionary[f"block{block}"][f"trial{trial}"]:
        Logger.print_and_log(f"=====================")
        Logger.print_and_log(f"Neurofeedback Score: {Data_Dictionary[f'block{block}'][f'trial{trial}']['nf_score']}")
        Logger.print_and_log(f"Residual Mean Score: {Data_Dictionary[f'block{block}'][f'trial{trial}']['resid_mean']}")
        Logger.print_and_log(f"=====================")
    return dictionary

""" SESSION SETUP """
# Setup Experimental Variables
Data_Dictionary: dict = ScriptManager.start_session(dictionary=Data_Dictionary)
starting_block_num: int = Settings.STARTING_BLOCK_NUM
block: int = starting_block_num - 1

# Setup Screen
pygame.init()  # initialize Pygame
Data_Dictionary, screen = Projector.get_monitor_info(dictionary=Data_Dictionary)

Projector.initialize_screen(screen=screen, instructions=["Welcome To The Experiment!", "Please Wait ..."])
Projector.show_instructions(screen=screen, instructions=Settings.NFB_INSTRUCTIONS)  # Show Instructions

Logger.print_and_log("Running Main Calculation Script ... ")
RunningBlock: bool = True
while RunningBlock:
    block, Data_Dictionary = ScriptManager.block_setup(dictionary=Data_Dictionary, block=block)  # Block Setup Func

    for trial in range(1, Settings.NFB_N_TRIALS + 1):
        try:
            if Settings.START_REST_TRIAL <= trial < Settings.START_NF_TRIAL:  # nfb vs rest block
                Projector.show_fixation_cross(dictionary=Data_Dictionary, screen=screen)
            else:
                Data_Dictionary = Projector.project_nfb_trial(dictionary=Data_Dictionary, screen=screen)

            # Trial Setup
            Data_Dictionary = ScriptManager.trial_setup(dictionary=Data_Dictionary, trial=trial, block=block)

            # Wait for New Dicom
            Data_Dictionary = ScriptManager.wait_for_new_dicom(dictionary=Data_Dictionary)

            # Run Trial
            run_trial(trial=trial, block=block, dictionary=Data_Dictionary)

            # End Trial
            Data_Dictionary = ScriptManager.end_trial(dictionary=Data_Dictionary, block=block, trial=trial)

            # Check if Block Should End
            Data_Dictionary, EndBlock = ScriptManager.check_to_end_block(dictionary=Data_Dictionary, trial=trial, screen=screen)
            if EndBlock:
                break  # break current for loop, start new block

        except KeyboardInterrupt as e:
            Data_Dictionary, EndBlock = ScriptManager.keyboard_stop(dictionary=Data_Dictionary, trial=trial, block=block, screen=screen)
            if EndBlock:
                break  # break current for loop, start new block

# End Script
ScriptManager.end_session(dictionary=Data_Dictionary, screen=screen)
