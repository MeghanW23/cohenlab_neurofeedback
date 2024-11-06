import sys
import pygame
import random
import time
import settings
import ScriptManager
import Projector
import Logger
import pandas as pd 
#!/usr/bin/env python3

pygame.init()  # initialize Pygame
print("This Task is a Stop Task Aimed at activating the rIFG and ACC.")
""" PATHS """
buzz: pygame.Surface = pygame.image.load(settings.BUZZ_PATH)
bear: pygame.Surface = pygame.image.load(settings.BEAR_PATH)
pressed_a: pygame.Surface = pygame.image.load(settings.PRESSED_A_PATH)
default_output_log_directory: str = settings.RIFG_LOG_DIR

""" FUNCTIONS """
def setup_seed_and_log_file(data_dictionary: dict) -> tuple:
    # Ask if the task is pre or post rIFG and set the appropriate seed
    while True:
        task_type: str = input("Run pre or post rIFG? (pre/post): ")
        if task_type == "pre":
            Logger.print_and_log("Ok, running pre-rIFG task ...")
            data_dictionary["whole_session_data"]["task_type"] = task_type
            random.seed(settings.RIFG_PRE_SEED)  # Set the seed for pre-task
            Logger.print_and_log(f"Seed set to {settings.RIFG_PRE_SEED} for pre-rIFG task.")
            event_csv = pd.read_csv(settings.PRE_RIFG_EVENT_CSV, delimiter=",")
            break

        elif task_type == "post":
            Logger.print_and_log("Ok, running post-rIFG task ...")
            data_dictionary["whole_session_data"]["task_type"] = task_type
            random.seed(settings.RIFG_POST_SEED)  # Set the seed for post-task
            Logger.print_and_log(f"Seed set to {settings.RIFG_POST_SEED} for post-rIFG task.")
            event_csv = pd.read_csv(settings.POST_RIFG_EVENT_CSV, delimiter=",")

            break

        else:
            Logger.print_and_log("Please type either 'pre' or 'post'. Try again.")
    
    # get ISI list
    onset_times = event_csv["onset"].to_list()
    trial_onset_times = onset_times[1:-1]
    ISI_list: list[float] = [0, ]
    for index, _ in enumerate(trial_onset_times):
        if index + 1 >= len(trial_onset_times):
            continue
        else:
            this_trial_onset = trial_onset_times[index]
            next_trial_onset = trial_onset_times[index + 1]
            ISI = next_trial_onset - (this_trial_onset + settings.RIFG_TRIAL_DURATION)
            ISI_list.append(ISI)

    # Create the CSV log file with the task type (pre/post) in the log file name
    log_name = f"{data_dictionary['whole_session_data']['pid']}_rifg_task_{task_type}.csv"
    csv_log_path = Logger.create_log(filetype=".csv", log_name=log_name)

    return csv_log_path, data_dictionary, ISI_list  # Return both csv_log_path and DataDictionary

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
    trial_dictionary: dict = DataDictionary[f"trial{trial_number}"]  # pull this trial's dictionary from main dictionary
    pressed_a_counter: int = 0  # count times 'a' is pressed

    start_time: float = time.time()  # Record the start time

    conditions_list: list = ["buzz", "buzz", "buzz", "bear"]  # Participants have a 75% chance of getting Buzz
    random.shuffle(conditions_list)
    stimulus: str = random.choice(conditions_list)  # chose random condition from conditions_list
    Logger.print_and_log(f"trial_type:{stimulus}")

    # record info on trial to dictionary
    trial_dictionary["trial_type"] = stimulus
    trial_dictionary["start_time"] = start_time

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
                    trial_dictionary["time_to_first_a_press"] = elapsed_time

                # pull screen information from data dictionary
                press_a_width: float = DataDictionary["whole_session_data"]["press_a_width"]
                press_a_height: float = DataDictionary["whole_session_data"]["press_a_height"]

                # show "pressed 'a'" image if 'a' is pressed
                screen.blit(pressed_a_resized, (settings.SECOND_MONITOR_WIDTH // settings.KEYPRESS_LOCATION_SECMON_WIDTH_DIVISOR - press_a_width // settings.KEYPRESS_LOCATION_WIDTH_DIVISOR, settings.SECOND_MONITOR_HEIGHT // settings.KEYPRESS_LOCATION_SECMON_HEIGHT_DIVISOR - press_a_height // settings.KEYPRESS_LOCATION_HEIGHT_DIVISOR))  # report keypress 'a'

                pygame.display.flip()

                # record trial results if 'a' was pressed
                if stimulus == "buzz":
                    trial_dictionary["result"] = "hit"

                elif stimulus == "bear":
                    trial_dictionary["result"] = "false alarm"

                break

        current_time: float = time.time()  # Get the current time
        elapsed_time: float = current_time - start_time  # Calculate elapsed time
        if elapsed_time >= settings.RIFG_TRIAL_DURATION:  # Check if trial duration has passed
            # record trial results if it wasn't ever pressed in the one-second time limit
            trial_dictionary["pressed_a_num_of_times"] = pressed_a_counter
            if pressed_a_counter == 0:
                if stimulus == "buzz":
                    trial_dictionary["result"] = "miss"
                elif stimulus == "bear":
                    trial_dictionary["result"] = "correct rejection"

            Logger.print_and_log("Half a second has passed.")
            trial_dictionary["half_second_has_passed"] = True
            break

    return DataDictionary

def blit_trial(stimulus):
    """
    Displays a specific stimulus on the screen based on the trial's stimulus type.
    """
    if stimulus == "buzz":
        buzz_width: float = DataDictionary["whole_session_data"]["buzz_width"]
        buzz_height: float = DataDictionary["whole_session_data"]["buzz_height"]
        screen.blit(buzz_resized, (settings.SECOND_MONITOR_WIDTH // settings.BUZZ_BEAR_LOCATION_SECMON_WIDTH_DIVISOR - buzz_width // settings.BUZZ_BEAR_LOCATION_WIDTH_DIVISOR, settings.SECOND_MONITOR_HEIGHT // settings.BUZZ_BEAR_LOCATION_SECMON_HEIGHT_DIVISOR - buzz_height // settings.BUZZ_BEAR_LOCATION_HEIGHT_DIVISOR))
        pygame.display.flip()
    else:
        bear_width: float = DataDictionary["whole_session_data"]["bear_width"]
        bear_height: float = DataDictionary["whole_session_data"]["bear_height"]
        screen.blit(bear_resized, (settings.SECOND_MONITOR_WIDTH // settings.BUZZ_BEAR_LOCATION_SECMON_WIDTH_DIVISOR - bear_width // settings.BUZZ_BEAR_LOCATION_WIDTH_DIVISOR, settings.SECOND_MONITOR_HEIGHT // settings.BUZZ_BEAR_LOCATION_SECMON_HEIGHT_DIVISOR - bear_height // settings.BUZZ_BEAR_LOCATION_HEIGHT_DIVISOR))
        pygame.display.flip()

    return None


""" SETUP """
# Ensure the whole_session_data dictionary is initialized correctly
DataDictionary: dict = {'whole_session_data': {}}
csv_log_path = None

# Debug: Check if DataDictionary is initialized properly
if DataDictionary["whole_session_data"] is None:
    raise ValueError("DataDictionary['whole_session_data'] is None after initialization")

# Start the session
ScriptManager.start_session(dictionary=DataDictionary)

# Debug: Check if start_session modifies DataDictionary
if DataDictionary is None or DataDictionary.get("whole_session_data") is None:
    raise ValueError("DataDictionary became None after ScriptManager.start_session")

# Set seed and log file based on PRE or POST task
csv_log_path, DataDictionary, ISI_list = setup_seed_and_log_file(DataDictionary)  # Unpack both values here

# Debug: Check if setup_seed_and_log_file modifies DataDictionary
if DataDictionary is None or DataDictionary.get("whole_session_data") is None:
    raise ValueError("DataDictionary became None after setup_seed_and_log_file")


# Dynamically detect and align the second monitor
DataDictionary, screen = Projector.get_monitor_info(dictionary=DataDictionary)

# Log screen dimensions and offsets
Logger.print_and_log(f"Second monitor resolution: {DataDictionary['whole_session_data']['second_monitor_width']}x{DataDictionary['whole_session_data']['second_monitor_height']}")
Logger.print_and_log(f"Offsets: X={DataDictionary['whole_session_data']['monitor_X_OFFSET']}, Y={DataDictionary['whole_session_data']['monitor_Y_OFFSET']}")

# Debug: Check after get_monitor_info
if DataDictionary is None or DataDictionary.get("whole_session_data") is None:
    raise ValueError("DataDictionary became None after Projector.get_monitor_info")


# Resize Loaded Pygame images
new_width_buzz: float = settings.SECOND_MONITOR_WIDTH // settings.BUZZ_WIDTH_DIVISOR  # Desired width for buzz
new_height_buzz: float = settings.SECOND_MONITOR_HEIGHT // settings.BUZZ_HEIGHT_DIVISOR  # Desired height for buzz
buzz_resized: pygame.Surface = pygame.transform.scale(buzz, (new_width_buzz, new_height_buzz))

# Check if "whole_session_data" exists before assigning values
if "whole_session_data" not in DataDictionary or DataDictionary["whole_session_data"] is None:
    raise ValueError("DataDictionary['whole_session_data'] is missing or None before resizing images.")

# Now assign values to the DataDictionary
buzz_width: float = buzz_resized.get_width()
buzz_height: float = buzz_resized.get_height()
DataDictionary["whole_session_data"]["buzz_width"] = buzz_width
DataDictionary["whole_session_data"]["buzz_height"] = buzz_height

new_width_bear: float = settings.SECOND_MONITOR_WIDTH // settings.BEAR_WIDTH_DIVISOR
new_height_bear: float = settings.SECOND_MONITOR_HEIGHT // settings.BEAR_HEIGHT_DIVISOR
bear_resized: pygame.Surface = pygame.transform.scale(bear, (new_width_bear, new_height_bear))

bear_width: float = bear_resized.get_width()
bear_height: float = bear_resized.get_height()
DataDictionary["whole_session_data"]["bear_width"] = bear_width
DataDictionary["whole_session_data"]["bear_height"] = bear_height

new_width_keypress: float = settings.KEYPRESS_WIDTH
new_height_keypress: float = settings.KEYPRESS_HEIGHT
pressed_a_resized: pygame.Surface = pygame.transform.scale(pressed_a, (new_width_keypress, new_height_keypress))

press_a_width: float = pressed_a_resized.get_width()
press_a_height: float = pressed_a_resized.get_height()
DataDictionary["whole_session_data"]["press_a_width"] = press_a_width
DataDictionary["whole_session_data"]["press_a_height"] = press_a_height

print_data_dictionary(DataDictionary, dictionary_name="All Session Data")  # print session data to terminal

Projector.initialize_screen(screen=screen, instructions=["Welcome To The Experiment!", "Please Wait ..."])
Projector.show_instructions(screen=screen, instructions=settings.RIFG_INSTRUCTIONS)  # Show Instructions

Projector.show_fixation_cross_rest(screen=screen, dictionary=DataDictionary, Get_CSV_if_Error=True)  # rest period of 30 sec showing fixation cross
pygame.display.flip()

try:
    # Run Each Trial
    for trial in range(1, settings.RIFG_N_TRIALS + 1):
        try:
            # Check for events (including keypresses)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    raise KeyboardInterrupt("Quit key pressed")

            Logger.print_and_log(f" ==== Starting Trial {trial} ==== ")

            # make a sub-dictionary in the data dictionary for this trial
            DataDictionary[f"trial{trial}"] = {}
            trial_dictionary = DataDictionary[f"trial{trial}"]

            Projector.show_fixation_cross(dictionary=DataDictionary, screen=screen)
            pygame.display.flip()  # flip to monitor

            Logger.print_and_log(f"Sleeping for interstimulus interval {ISI_list[trial - 1]}")
            time.sleep(ISI_list[trial - 1])
            pygame.event.clear()

            DataDictionary = handle_trial(DataDictionary=DataDictionary, trial_number=trial)   # Run the Buzz/Bear Part of Trial

            print_data_dictionary(trial_dictionary)  # print the data to the terminal

        except KeyboardInterrupt:
            Logger.print_and_log("Quit Session.")
            break  # Exit the trial loop upon quit

finally:
    if csv_log_path:
        # Update the existing CSV log file using the path created earlier
        Logger.update_log(log_name=csv_log_path, dictionary_to_write=DataDictionary)

        Projector.show_fixation_cross_rest(screen=screen, dictionary=DataDictionary, Get_CSV_if_Error=True)
        pygame.display.flip()

    # Ensure the task ends properly with an "ending_cause"
    if "ending_cause" not in DataDictionary['whole_session_data'] or DataDictionary['whole_session_data']['ending_cause'] != "keyboard_interrupt":
        DataDictionary['whole_session_data']['ending_cause'] = "undocumented or regular"

    if csv_log_path:
        # Update the same CSV log file again with the final state
        Logger.update_log(log_name=csv_log_path, dictionary_to_write=DataDictionary)

    Projector.show_end_message(screen=screen)