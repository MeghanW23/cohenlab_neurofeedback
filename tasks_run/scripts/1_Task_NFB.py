import sys
import FileHandler
import Calculator
import Logger
import settings
import ScriptManager
import Projector
import pygame
import time 
import warnings
from datetime import datetime 

Data_Dictionary: dict = {'whole_session_data': {}}
""" FUNCTIONS """
@ScriptManager.retry_if_error(dictionary=Data_Dictionary)
def run_trial(trial: int, block: int, dictionary: dict) -> dict:
    ScriptManager.check_dicom_rerun(dictionary=dictionary,
                                    block=block,
                                    trial=trial)

    dictionary[f"block{block}"][f"trial{trial}"]["dicom_path"] = FileHandler.get_most_recent(action="dicom",
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
            dictionary[f"block{block}"]["nf_scores"] = [dictionary[f"block{block}"][f"trial{trial}"]["normalized_mean_activation"]]

        else:
            dictionary[f"block{block}"]["nf_scores"].append(dictionary[f"block{block}"][f"trial{trial}"]["normalized_mean_activation"])

    elif settings.NFB_FROM_RESIDUAL_VALUE:
        if "nf_scores" not in dictionary[f"block{block}"]:
            dictionary[f"block{block}"]["nf_scores"] = [
                dictionary[f"block{block}"][f"trial{trial}"]["normalized_resid_mean"]]

        else:
            dictionary[f"block{block}"]["nf_scores"].append(
                dictionary[f"block{block}"][f"trial{trial}"]["normalized_resid_mean"])

    else:
        Logger.print_and_log(f"Enter what type of calculation you want to use to make the nfb score in settings and then update this script.")
        sys.exit(1)
    
    Logger.update_score_csv(action="add_to_csv",
                            task="nfb",
                            path_to_csv=score_csv_path,
                            score=dictionary[f"block{block}"]["nf_scores"][-1],
                            tr=int(trial),
                            additional_data=[Data_Dictionary["whole_session_data"]["total_trials"], 
                                             block, 
                                             Data_Dictionary[f"block{block}"][f"trial{trial}"]["mean_activation"]]
                            )
    return dictionary

""" SESSION SETUP """
if settings.IGNORE_WARNINGS:
    warnings.filterwarnings("ignore")

# Setup Experimental Variables
pygame.init()  # initialize Pygame
Data_Dictionary: dict = ScriptManager.start_session(dictionary=Data_Dictionary)
block: int = settings.STARTING_BLOCK_NUM - 1
Data_Dictionary["whole_session_data"]["total_trials"] = 0
score_csv_path = Logger.update_score_csv(action="create_csv",
                                         task="nfb",
                                         path_to_csv_dir=settings.NFB_SCORE_LOG_DIR,
                                         pid=Data_Dictionary["whole_session_data"]["pid"],
                                         additional_headers=["total_trials", "block_num", "mean_activation"])
# Setup Screen
Data_Dictionary, screen = Projector.get_monitor_info(dictionary=Data_Dictionary)

Projector.initialize_screen(screen=screen, instructions=["Welcome To The Experiment!", "Please Wait ..."], dictionary=Data_Dictionary)
Projector.show_instructions(screen=screen, instructions=settings.NFB_INSTRUCTIONS)  # Show Instructions

Logger.print_and_log("Running Main Calculation Script ... ")
RunningBlock: bool = True
while RunningBlock:
    block, Data_Dictionary = ScriptManager.block_setup(dictionary=Data_Dictionary, block=block, screen=screen)  # Block Setup Func
    Data_Dictionary = Projector.setup_nfb_icons(dictionary=Data_Dictionary)

    if block % 2 == 0:
        n_trials: int = settings.NFB_N_TRIALS_EVEN_BLOCK
    else:
        n_trials: int = settings.NFB_N_TRIALS_ODD_BLOCK

    start_time = datetime.now()
    for trial in range(1, n_trials + 1):
        Data_Dictionary["whole_session_data"]["total_trials"] += 1
        # get last loops total time 
        Logger.print_and_log(f"Time taken: {datetime.now() - start_time}")
        start_time = datetime.now()
        
        try:
            # Check for events (including keypresses)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    raise KeyboardInterrupt("Quit key pressed")

            if trial == 1:
                time.sleep(1) # wait for dir permissions to be set if they need to be 

            # Trial Setup
            Data_Dictionary = ScriptManager.trial_setup(dictionary=Data_Dictionary, trial=trial, block=block)

            # Wait for New Dicom
            Data_Dictionary = ScriptManager.wait_for_new_dicom(dictionary=Data_Dictionary)

            # Run Trial
            Data_Dictionary = run_trial(trial=trial, block=block, dictionary=Data_Dictionary)


            if settings.START_REST_TRIAL <= trial < settings.START_NF_TRIAL:  # nfb vs rest block
                Logger.print_and_log("Showing Rest Block")
                Projector.show_fixation_cross(dictionary=Data_Dictionary, screen=screen)
            elif n_trials == settings.NFB_N_TRIALS_EVEN_BLOCK and trial >= settings.EVEN_BLOCK_START_2ND_REST:
                Logger.print_and_log("Showing Rest Block")
                Projector.show_fixation_cross(dictionary=Data_Dictionary, screen=screen)
            else:
                Logger.print_and_log("Showing NFB Block")
                Data_Dictionary = Projector.project_nfb_trial(dictionary=Data_Dictionary, screen=screen, block=block, trial=trial)

            # End Trial
            Data_Dictionary = ScriptManager.end_trial(dictionary=Data_Dictionary, block=block, trial=trial)

            # Check if Block Should End
            Data_Dictionary, EndBlock = ScriptManager.check_to_end_block(dictionary=Data_Dictionary, trial=trial, screen=screen, block_num=block)
            if EndBlock:
                break  # break current for loop, start new block

        except KeyboardInterrupt as e:
            Logger.print_and_log("---- Keyboard Interrupt Detected ----")
            Projector.show_message(screen=screen, message=settings.INTER_TRIAL_MESSAGE)
            Data_Dictionary, EndBlock = ScriptManager.keyboard_stop(dictionary=Data_Dictionary, trial=trial, block=block, screen=screen)
            if EndBlock:
                break  # break current for loop, start new block

# End Script
ScriptManager.end_session(dictionary=Data_Dictionary, screen=screen)
