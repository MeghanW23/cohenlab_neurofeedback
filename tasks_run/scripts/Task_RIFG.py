import os
import sys
import pygame
import random
import time
import settings
import ScriptManager
import Projector
import Logger

pygame.init()  # initialize Pygame
print("This Task is a Stop Task Aimed at activating the rIFG and ACC.")

""" PATHS """
buzz: pygame.Surface = pygame.image.load(settings.BUZZ_PATH)
bear: pygame.Surface = pygame.image.load(settings.BEAR_PATH)
pressed_a: pygame.Surface = pygame.image.load(settings.PRESSED_A_PATH)
default_output_log_directory: str = settings.RIFG_LOG_DIR
""" FUNCTIONS """
def print_data_dictionary(dictionary: dict, dictionary_name: str = None) -> None:
    if dictionary_name is not None:
        Logger.print_and_log("\n---")
        Logger.print_and_log(f"Printing Info on {dictionary_name} Below: ")
    else:
        Logger.print_and_log(f"Printing Dictionary Information Below: \n")

    for key, value in dictionary.items():
        Logger.print_and_log("---")

        if isinstance(dictionary[key], dict):  # if this key in the dictionary is a sub-dictionary, format a different way
            Logger.print_and_log(f"dictionary: {key}")
            for subkey, subvalue in dictionary[key].items():
                Logger.print_and_log(f"  {subkey}: {subvalue}")
        else:
            Logger.print_and_log(f"key: {key}, value: {value}")

    Logger.print_and_log("---\n")

def handle_trial(DataDictionary: dict, trial_number: int) -> dict:
    SECOND_MONITOR_WIDTH = float(os.getenv("SECOND_MONITOR_WIDTH"))
    SECOND_MONITOR_HEIGHT = float(os.getenv("SECOND_MONITOR_HEIGHT"))


    trial_dictionary: dict = DataDictionary[f"trial{trial_number}"]  # pull this trial's dictionary from main dictionary
    pressed_a_counter: int = 0  # count times 'a' is pressed

    start_time: float = time.time()  # Record the start time

    conditions_list: list = ["buzz", "buzz", "buzz", "bear"]  # Participants have a 75% chance of getting Buzz
    random.shuffle(conditions_list)
    stimulus: str = random.choice(conditions_list)  # chose random condition from conditions_list
    Logger.print_and_log(f"trial_type:{stimulus}")

    # record info on trial to dictionary
    trial_dictionary["trial_type"]: str = stimulus
    trial_dictionary["start_time"]: float = start_time

    while True:
        blit_trial(stimulus=stimulus)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                Logger.print_and_log("Pressed A")

                pressed_a_counter += 1

                if pressed_a_counter == 1:
                    # get reaction time
                    current_time: float = time.time()  # Get the current time
                    elapsed_time: float = current_time - start_time  # Calculate elapsed time
                    trial_dictionary["time_to_first_a_press"]: float = elapsed_time

                # pull screen information from data dictionary
                press_a_width: float = DataDictionary["whole_session_data"]["press_a_width"]
                press_a_height: float = DataDictionary["whole_session_data"]["press_a_height"]

                # show "pressed 'a'" image if 'a' is pressed
                screen.blit(pressed_a_resized, (SECOND_MONITOR_WIDTH // settings.KEYPRESS_LOCATION_SECMON_WIDTH_DIVISOR - press_a_width // settings.KEYPRESS_LOCATION_WIDTH_DIVISOR, SECOND_MONITOR_HEIGHT // settings.KEYPRESS_LOCATION_SECMON_HEIGHT_DIVISOR - press_a_height // settings.KEYPRESS_LOCATION_HEIGHT_DIVISOR))  # report keypress 'a'

                pygame.display.flip()

                # record trial results if 'a' was pressed
                if stimulus == "buzz":
                    trial_dictionary["result"]: str = "hit"

                elif stimulus == "bear":
                    trial_dictionary["result"]: str = "false alarm"

                break

        current_time: float = time.time()  # Get the current time
        elapsed_time: float = current_time - start_time  # Calculate elapsed time
        if elapsed_time >= 0.5:  # Check if half a second has passed
            # record trial results if it wasn't ever pressed in the one-second time limit
            trial_dictionary["pressed_a_num_of_times"]: int = pressed_a_counter
            if pressed_a_counter == 0:
                if stimulus == "buzz":
                    trial_dictionary["result"]: str = "miss"
                elif stimulus == "bear":
                    trial_dictionary["result"]: str = "correct rejection"

            Logger.print_and_log("Half a second has passed.")
            trial_dictionary["half_second_has_passed"] = True
            break

    return DataDictionary

def blit_trial(stimulus):
    SECOND_MONITOR_WIDTH = float(os.getenv("SECOND_MONITOR_WIDTH"))
    SECOND_MONITOR_HEIGHT = float(os.getenv("SECOND_MONITOR_HEIGHT"))

    """
    Displays a specific stimulus on the screen based on the trial's stimulus type.

    Depending on whether the stimulus is "buzz" or "bear," this function blits (renders)
    the corresponding image onto the screen at a specified position. The function handles
    the display update and positioning based on the screen dimensions provided in the
    `DataDictionary`.

    Args:
        stimulus (str): The type of stimulus to display. It should be either "buzz" or "bear".

    Returns:
        None

    Example:
        If the stimulus is "buzz", the function will:
        1. Retrieve the dimensions for the buzz image from `DataDictionary`.
        2. Calculate the position to center the buzz image on the screen.
        3. Render the buzz image at the calculated position and update the display.

        Similarly, if the stimulus is "bear", the function will perform the same steps
        but for the bear image.

    The function assumes that the Pygame environment is properly initialized and that
    the `screen`, `buzz_resized`, and `bear_resized` variables are defined and contain
    the images to be displayed.
    """
    # blit image using information on image sizes from data dictionary
    if stimulus == "buzz":
        buzz_width: float = DataDictionary["whole_session_data"]["buzz_width"]
        buzz_height: float = DataDictionary["whole_session_data"]["buzz_height"]
        screen.blit(buzz_resized, (SECOND_MONITOR_WIDTH // settings.BUZZ_BEAR_LOCATION_SECMON_WIDTH_DIVISOR - buzz_width // settings.BUZZ_BEAR_LOCATION_WIDTH_DIVISOR, SECOND_MONITOR_HEIGHT // settings.BUZZ_BEAR_LOCATION_SECMON_HEIGHT_DIVISOR - buzz_height // settings.BUZZ_BEAR_LOCATION_HEIGHT_DIVISOR))

        pygame.display.flip()
    else:
        bear_width: float = DataDictionary["whole_session_data"]["bear_width"]
        bear_height: float = DataDictionary["whole_session_data"]["bear_height"]
        screen.blit(bear_resized, (SECOND_MONITOR_WIDTH // settings.BUZZ_BEAR_LOCATION_SECMON_WIDTH_DIVISOR - bear_width // settings.BUZZ_BEAR_LOCATION_WIDTH_DIVISOR, SECOND_MONITOR_HEIGHT // settings.BUZZ_BEAR_LOCATION_SECMON_HEIGHT_DIVISOR - bear_height // settings.BUZZ_BEAR_LOCATION_HEIGHT_DIVISOR))

        pygame.display.flip()

    return None


""" SETUP """
SECOND_MONITOR_WIDTH = float(os.getenv("SECOND_MONITOR_WIDTH"))
SECOND_MONITOR_HEIGHT = float(os.getenv("SECOND_MONITOR_HEIGHT"))
DataDictionary: dict = {'whole_session_data': {}}
ScriptManager.start_session(dictionary=DataDictionary)
DataDictionary, screen = Projector.get_monitor_info(dictionary=DataDictionary)
random.seed(settings.RANDOM_SEED_VALUE)


# Resize Loaded Pygame images
new_width_buzz: float = SECOND_MONITOR_WIDTH // settings.BUZZ_WIDTH_DIVISOR  # Desired width for buzz
new_height_buzz: float = SECOND_MONITOR_HEIGHT // settings.BUZZ_HEIGHT_DIVISOR  # Desired height for buzz
buzz_resized: pygame.Surface = pygame.transform.scale(buzz, (new_width_buzz, new_height_buzz))
buzz_width: float = buzz_resized.get_width()
buzz_height: float = buzz_resized.get_height()
DataDictionary["whole_session_data"]["buzz_width"]: float = buzz_width
DataDictionary["whole_session_data"]["buzz_height"]: float = buzz_height


new_width_bear: float = SECOND_MONITOR_WIDTH // settings.BEAR_WIDTH_DIVISOR
new_height_bear: float = SECOND_MONITOR_HEIGHT // settings.BEAR_HEIGHT_DIVISOR
bear_resized: pygame.Surface = pygame.transform.scale(bear, (new_width_bear, new_height_bear))
bear_width: float = bear_resized.get_width()
bear_height: float = bear_resized.get_height()
DataDictionary["whole_session_data"]["bear_width"]: float = bear_width
DataDictionary["whole_session_data"]["bear_height"]: float = bear_height

new_width_keypress: float = settings.KEYPRESS_WIDTH
new_height_keypress: float = settings.KEYPRESS_HEIGHT
pressed_a_resized: pygame.Surface = pygame.transform.scale(pressed_a, (new_width_keypress, new_height_keypress))
press_a_width: float = pressed_a_resized.get_width()
press_a_height: float = pressed_a_resized.get_height()
DataDictionary["whole_session_data"]["press_a_width"]: float = press_a_width
DataDictionary["whole_session_data"]["press_a_height"]: float = press_a_height


print_data_dictionary(DataDictionary, dictionary_name="All Session Data")  # print session data to terminal

Projector.initialize_screen(screen=screen, instructions=["Welcome To The Experiment!", "Please Wait ..."])
Projector.show_instructions(screen=screen, instructions=settings.RIFG_INSTRUCTIONS)  # Show Instructions

Projector.show_fixation_cross_rest(screen=screen, dictionary=DataDictionary, Get_CSV_if_Error=True)  # rest period of 30 sec showing fixation cross
pygame.display.flip()

# Run Each Trial
for trial in range(1, settings.RIFG_N_TRIALS + 1):
    try:
        # Check for events (including keypresses)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                raise KeyboardInterrupt("Quit key pressed")

        Logger.print_and_log(f" ==== Starting Trial {trial} ==== ")

        # make a sub-dictionary in the data dictionary for this trial
        DataDictionary[f"trial{trial}"]: dict = {}
        trial_dictionary = DataDictionary[f"trial{trial}"]


        Projector.show_fixation_cross(dictionary=DataDictionary, screen=screen)

        pygame.display.flip()  # flip to monitor

        ISI: int = random.randrange(start=settings.ISI_MIN, stop=settings.ISI_MAX, step=settings.ISI_STEP)  # get random inter stimulus interval (in ms)
        Logger.print_and_log(f"ISI: {ISI}")
        trial_dictionary["ISI"] = ISI  # add ISI to trial_dictionary

        time.sleep(ISI / 1000.0)  # do the ISI wait time

        DataDictionary = handle_trial(DataDictionary=DataDictionary, trial_number=trial)   # Run the Buzz/Bear Part of Trial

        print_data_dictionary(trial_dictionary)  # print the data to the terminal


    except KeyboardInterrupt as e:
        DataDictionary['whole_session_data']['ending_cause']: str = "keyboard_interrupt"
        Logger.print_and_log("Quit Session.")
        csv_log: str = Logger.create_log(filetype=".csv", log_name=f"{DataDictionary['whole_session_data']['pid']}_rifg_task")
        Logger.update_log(log_name=csv_log, dictionary_to_write=DataDictionary)
        sys.exit(1)

Projector.show_fixation_cross_rest(screen=screen, dictionary=DataDictionary, Get_CSV_if_Error=True)
pygame.display.flip()

if "ending_cause" not in DataDictionary['whole_session_data'] or not "keyboard_interrupt" != DataDictionary['whole_session_data']['ending_cause']:
    DataDictionary['whole_session_data']['ending_cause']: str = "undocumented or regular"
    csv_log: str = Logger.create_log(filetype=".csv",
                                     log_name=f"{DataDictionary['whole_session_data']['pid']}_rifg_task")
    Logger.update_log(log_name=csv_log, dictionary_to_write=DataDictionary)


Projector.show_end_message(screen=screen)
