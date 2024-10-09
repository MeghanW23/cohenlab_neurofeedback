import pygame
import settings
import Logger
import time
import ScriptManager
import random
import Projector

def get_settings_and_log(data_dictionary: dict) -> dict:
    data_dictionary["whole_session_data"]["pid"] = ScriptManager.get_participant_id()
    Logger.create_log(filetype=".txt", log_name=f"{data_dictionary['whole_session_data']['pid']}_MSIT_PRE") # create text output log

    while True:
        practice_block_str: str = input("Is this a practice block? (y/n): ")
        if practice_block_str == "y":
            Logger.print_and_log("Ok, running practice block ...")
            data_dictionary["whole_session_data"]["practice_block"] = True
            break

        elif practice_block_str == "n":
            Logger.print_and_log("Ok, running practice block ...")
            data_dictionary["whole_session_data"]["practice_block"] = False
            break

        else:
            Logger.print_and_log("Please type either 'y' or 'n'. Try again.")

    while True:
        msit_type: str = input("Run pre or post MSIT? (pre/post): ")
        if msit_type == "pre":
            Logger.print_and_log("Ok, running pre-msit task ...")
            data_dictionary["whole_session_data"]["msit_type"] = msit_type
            break

        elif msit_type == "post":
            Logger.print_and_log("Ok, running post-msit task ...")
            data_dictionary["whole_session_data"]["msit_type"] = msit_type
            break

        else:
            Logger.print_and_log("Please type either 'pre' or 'post'. Try again.")

    while True:
        starting_block_type: str = input("Run interference or control block first? (i/c): ")
        if starting_block_type == "i":
            Logger.print_and_log("Ok, starting with interference block ...")
            data_dictionary["whole_session_data"]["starting_block_type"] = starting_block_type
            break

        elif starting_block_type == "c":
            Logger.print_and_log("Ok, starting with control block ...")
            data_dictionary["whole_session_data"]["starting_block_type"] = starting_block_type
            break

        else:
            Logger.print_and_log("Please type either 'i' or 'c'. Try again.")

    return data_dictionary
def run_msit_task():
    pygame.init() # initialize task

    Data_Dictionary = {'whole_session_data': {}} # create whole session dictionary

    Data_Dictionary = get_settings_and_log(data_dictionary=Data_Dictionary)

    number_font = pygame.font.Font(None, settings.MSIT_FONT_SIZE_NUMBERS) # get font size
    random.seed(settings.RANDOM_SEED_VALUE)  # get seed value

    # get screen information
    try:
        Data_Dictionary, screen = Projector.get_monitor_info(dictionary=Data_Dictionary)
        screen_width = Data_Dictionary["whole_session_data"]["second_monitor_width"]
        screen_height = Data_Dictionary["whole_session_data"]["second_monitor_height"]
    except KeyError:
        Logger.print_and_log("No second monitor detected, using local screen.")
        screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
        screen = pygame.display.set_mode((screen_width, screen_height))

    # show instructions
    Projector.initialize_screen(screen=screen, instructions=settings.MSIT_INSTRUCTIONS)
    Projector.show_instructions(screen=screen, instructions=settings.MSIT_INSTRUCTIONS)

    # show 30s rest
    Projector.show_fixation_cross_rest(screen=screen, dictionary=Data_Dictionary, Get_CSV_if_Error=True)

    # loop through each block
    for block_num in range(1, settings.MSIT_NUM_BLOCKS + 1):
        Logger.print_and_log(f"Running {block_num} of {settings.MSIT_NUM_BLOCKS}")


run_msit_task()