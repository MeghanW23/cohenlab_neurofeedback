import pprint
import sys

import FileHandler
import Calculator
import Logger
import settings
import ScriptManager
import ProjectorMW
import pygame

Data_Dictionary: dict = {'whole_session_data': {}}
""" FUNCTIONS """
@ScriptManager.retry_if_error(dictionary=Data_Dictionary)
def run_trial(trial: int, block: int, dictionary: dict) -> dict:
    ScriptManager.check_dicom_rerun(dictionary=dictionary,
                                    block=block,
                                    trial=trial)

    dictionary[f"block{block}"][f"trial{trial}"]["dicom_path"]: str = FileHandler.get_most_recent(action="dicom",
                                                                                                  dicom_dir=dictionary["whole_session_data"]["dicom_dir_path"])
    Logger.print_and_log(f"Using DICOM:{dictionary[f'block{block}'][f'trial{trial}']['dicom_path']}")

    if dictionary[f"block{block}"][f"trial{trial}"]["this_trial_tries"] > 1:
        WaitAfterRun: bool = True
    else:
        WaitAfterRun: bool = False

    dictionary[f"block{block}"][f"trial{trial}"]["nifti_path"] = FileHandler.dicom_to_nifti(dicom_file=dictionary[f"block{block}"][f"trial{trial}"]["dicom_path"],
                                                                                            trial=trial,
                                                                                            WaitAfterRun=WaitAfterRun)

    dictionary = Calculator.get_mean_activation(dictionary=dictionary,
                                   roi_mask=dictionary["whole_session_data"]["roi_mask_path"],
                                   nifti_image_path=dictionary[f"block{block}"][f"trial{trial}"]["nifti_path"],
                                   block=block,
                                   trial=trial)

    dictionary = Calculator.get_resid(dictionary=dictionary,
                                      block=block,
                                      trial=trial)
    if settings.NFB_FROM_MEAN_ACTIVATION:
        if "nf_scores" not in dictionary[f"block{block}"]:
            dictionary[f"block{block}"]["nf_scores"]: list = [dictionary[f"block{block}"][f"trial{trial}"]["normalized_mean_activation"]]

        else:
            dictionary[f"block{block}"]["nf_scores"].append(dictionary[f"block{block}"][f"trial{trial}"]["normalized_mean_activation"])

    elif settings.NFB_FROM_RESIDUAL_VALUE:
        if "nf_scores" not in dictionary[f"block{block}"]:
            dictionary[f"block{block}"]["nf_scores"]: list = [
                dictionary[f"block{block}"][f"trial{trial}"]["normalized_resid_mean"]]

        else:
            dictionary[f"block{block}"]["nf_scores"].append(
                dictionary[f"block{block}"][f"trial{trial}"]["normalized_resid_mean"])

    else:
        Logger.print_and_log(f"Enter what type of calculation you want to use to make the nfb score in settings and then update this script.")
        sys.exit(1)

    return dictionary

""" SESSION SETUP """
# Setup Experimental Variables
Data_Dictionary: dict = ScriptManager.start_session(dictionary=Data_Dictionary)
starting_block_num: int = settings.STARTING_BLOCK_NUM
block: int = starting_block_num - 1

# Setup Screen
pygame.init()  # initialize Pygame
Data_Dictionary, screen = ProjectorMW.get_monitor_info(dictionary=Data_Dictionary)

ProjectorMW.initialize_screen(screen=screen, instructions=["Welcome To The Experiment!", "Please Wait ..."])
ProjectorMW.show_instructions(screen=screen, instructions=settings.NFB_INSTRUCTIONS)  # Show Instructions

Logger.print_and_log("Running Main Calculation Script ... ")
RunningBlock: bool = True
while RunningBlock:
    block, Data_Dictionary = ScriptManager.block_setup(dictionary=Data_Dictionary, block=block)  # Block Setup Func
    Data_Dictionary = ProjectorMW.setup_nfb_icons(dictionary=Data_Dictionary)

    for trial in range(1, settings.NFB_N_TRIALS + 1):
        try:
            # Check for events (including keypresses)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    raise KeyboardInterrupt("Quit key pressed")

            # Trial Setup
            Data_Dictionary = ScriptManager.trial_setup(dictionary=Data_Dictionary, trial=trial, block=block)

            # Wait for New Dicom
            Data_Dictionary = ScriptManager.wait_for_new_dicom(dictionary=Data_Dictionary)

            # Run Trial
            Data_Dictionary = run_trial(trial=trial, block=block, dictionary=Data_Dictionary)


            if settings.START_REST_TRIAL <= trial < settings.START_NF_TRIAL:  # nfb vs rest block
                ProjectorMW.show_fixation_cross(dictionary=Data_Dictionary, screen=screen)
            else:
                pprint.pprint(Data_Dictionary)
                Data_Dictionary = ProjectorMW.project_nfb_trial(dictionary=Data_Dictionary, screen=screen, block=block, trial=trial)

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
