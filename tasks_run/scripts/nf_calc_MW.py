import FileHandler
import Calculator
import Logger
import settings
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

    return dictionary

def setup_trial_projection(dictionary: dict):
    portal_image: pygame.Surface = pygame.image.load(settings.PORTAL_PATH)
    collision: pygame.Surface = pygame.image.load(settings.COLLISION_WORD_ART)
    streak: pygame.Surface = pygame.image.load(settings.HIGH_PERFORM_WORD_ART)
    print_bg: pygame.Surface = pygame.image.load(settings.PRINT_BACKGROUND)
    rocket_image: pygame.Surface = pygame.image.load(settings.ROCKET_PATH)
    rocket_image_flames: pygame.Surface = pygame.image.load(settings.ROCKET_WITH_FLAMES_PATH)

    rocket_image: pygame.Surface = pygame.transform.scale(rocket_image, (settings.rocket_width, settings.rocket_height))
    ball_image_flames = pygame.transform.scale(rocket_image_flames, (settings.rocket_flames_width, settings.rocket_flames_height))

    # Set initial position of the ball
    initial_ball_x = dictionary["whole_session_data"]["second_monitor_width"] // settings.INITIAL_ROCKET_LOCATION_SECMON_WIDTH_DIVISOR - settings.rocket_width // settings.ROCKET_WIDTH_LOCATION_DIVISOR
    ball_y = dictionary["whole_session_data"]["second_monitor_height"] // settings.INITIAL_ROCKET_LOCATION_SECMON_HEIGHT_DIVISOR - settings.rocket_height // settings.ROCKET_WIDTH_LOCATION_DIVISOR

    bg = pygame.transform.scale(pygame.image.load(settings.BACKGROUND_PATH_1).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))
    bg2 = pygame.transform.scale(pygame.image.load(settings.BACKGROUND_PATH_2).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))
    bg3 = pygame.transform.scale(pygame.image.load(settings.BACKGROUND_PATH_3).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))
    bg4 = pygame.transform.scale(pygame.image.load(settings.BACKGROUND_PATH_4).convert(), (dictionary["whole_session_data"]["second_monitor_width"], dictionary["whole_session_data"]["second_monitor_height"]))



""" SESSION SETUP """
# Setup Experimental Variables
Data_Dictionary: dict = ScriptManager.start_session(dictionary=Data_Dictionary)
starting_block_num: int = settings.STARTING_BLOCK_NUM
block: int = starting_block_num - 1

# Setup Screen
pygame.init()  # initialize Pygame
Data_Dictionary, screen = Projector.get_monitor_info(dictionary=Data_Dictionary)
Projector.initialize_screen(screen=screen, instructions=["Welcome To The Experiment!", "Please Wait ..."])
Projector.show_instructions(screen=screen, instructions=settings.NFB_INSTRUCTIONS)  # Show Instructions

Logger.print_and_log("Running Main Calculation Script ... ")
RunningBlock: bool = True
while RunningBlock:
    block, Data_Dictionary = ScriptManager.block_setup(dictionary=Data_Dictionary, block=block)  # Block Setup Func

    for trial in range(1, settings.NFB_N_TRIALS + 1):
        try:
            # Trial Setup
            Data_Dictionary = ScriptManager.trial_setup(dictionary=Data_Dictionary, trial=trial, block=block)

            # Wait for New Dicom
            Data_Dictionary = ScriptManager.wait_for_new_dicom(dictionary=Data_Dictionary)

            # Run Trial
            run_trial(trial=trial, block=block, dictionary=Data_Dictionary)

            # End Trial
            Data_Dictionary = ScriptManager.end_trial(dictionary=Data_Dictionary, block=block, trial=trial)

            # Check if Block Should End
            Data_Dictionary, EndBlock = ScriptManager.check_to_end_block(dictionary=Data_Dictionary, trial=trial)
            if EndBlock:
                break  # break current for loop, start new block

        except KeyboardInterrupt as e:
            Data_Dictionary, EndBlock = ScriptManager.keyboard_stop(dictionary=Data_Dictionary, trial=trial, block=block)
            if EndBlock:
                break  # break current for loop, start new block

# End Script
ScriptManager.end_session(dictionary=Data_Dictionary)
