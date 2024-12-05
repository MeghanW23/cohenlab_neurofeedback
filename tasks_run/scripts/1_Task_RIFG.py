import sys
import os
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
            break

        elif task_type == "post":
            Logger.print_and_log("Ok, running post-rIFG task ...")
            data_dictionary["whole_session_data"]["task_type"] = task_type
            random.seed(settings.RIFG_POST_SEED)  # Set the seed for post-task
            Logger.print_and_log(f"Seed set to {settings.RIFG_POST_SEED} for post-rIFG task.")
            break

        else:
            Logger.print_and_log("Please type either 'pre' or 'post'. Try again.")

    participant_id = data_dictionary["whole_session_data"]["pid"]
    session_num = data_dictionary["whole_session_data"].get("session_num", "01")
    event_csv_dir = settings.RIFG_EVENT_CSV_DIR  # Base directory
    os.makedirs(event_csv_dir, exist_ok=True)  # Ensure directory exists

    # Build the event file name
    event_csv_name = f"{participant_id}_rifg_task_session{session_num}_{task_type}RIFG_events.csv"
    event_csv_path = os.path.join(event_csv_dir, event_csv_name)

    # Initialize the event file
    Logger.print_and_log(f"Creating event file: {event_csv_path}")
    initial_event_df = pd.DataFrame(columns=["onset", "duration", "trial_type"])
    initial_event_df.to_csv(event_csv_path, index=False)

    # Create the log file for the task
    log_name = f"{participant_id}_rifg_task_{task_type}.csv"
    csv_log_path = Logger.create_log(filetype=".csv", log_name=log_name)

    # Set a constant ISI list (adjust duration if needed)
    ISI_list = [1.0] * settings.RIFG_N_TRIALS
    # df = pd.read_csv(/path/toISI.csv) 
    # time_to_sleep = df[trial - 1]
    # time.sleep(time_to_sleep)

    return csv_log_path, data_dictionary, ISI_list

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

def create_event_csv(event_csv_path, trial_data):
    """
    Updates the event CSV with trial data.
    :param event_csv_path: Path to the event CSV file.
    :param trial_data: Dictionary containing trial onset, duration, and trial_type.
    """
    event_df = pd.DataFrame([trial_data])
    try:
        # Append to the CSV file or create it if it doesn't exist
        event_df.to_csv(
            event_csv_path,
            mode='a',
            header=not pd.io.common.file_exists(event_csv_path),
            index=False
        )
    except Exception as e:
        Logger.print_and_log(f"Error writing to event CSV: {e}")


def handle_trial(DataDictionary: dict, trial_number: int, event_csv_path: str) -> dict:
    """
    Handles a single trial, recording participant responses and logging them into the event CSV.

    :param DataDictionary: The main dictionary containing task data.
    :param trial_number: The current trial number.
    :param event_csv_path: The path to the event CSV file.
    :return: Updated DataDictionary.
    """
    trial_dictionary = DataDictionary[f"trial{trial_number}"]  # Pull this trial's dictionary
    pressed_a_counter = 0  # Count the number of 'a' key presses
    start_time = time.time()  # Record the start time

    # Define the stimulus conditions
    conditions_list = ["buzz", "buzz", "buzz", "bear"]  # 75% chance of Buzz
    random.shuffle(conditions_list)
    stimulus = random.choice(conditions_list)  # Choose random condition from conditions_list
    Logger.print_and_log(f"trial_type: {stimulus}")

    # Record the trial type in the dictionary
    trial_dictionary["trial_type"] = stimulus
    trial_dictionary["start_time"] = start_time

    # Initialize trial data for the CSV
    trial_data = {
        "onset": round(DataDictionary["current_onset"], 1),  # Use task-relative onset time
        "duration": settings.RIFG_TRIAL_DURATION,
        "trial_type": None  # This will be determined based on participant response
    }

    while True:
        pygame.event.clear()  # Clear any accidental keypresses during fixation
        blit_trial(stimulus=stimulus)  # Display the stimulus

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                Logger.print_and_log("Pressed A")
                pressed_a_counter += 1

                if pressed_a_counter == 1:
                    elapsed_time = time.time() - start_time  # Calculate reaction time
                    trial_dictionary["time_to_first_a_press"] = elapsed_time

                # Display the feedback for key press
                screen.blit(
                    pressed_a_resized,
                    (
                        settings.SECOND_MONITOR_WIDTH // settings.KEYPRESS_LOCATION_SECMON_WIDTH_DIVISOR
                        - DataDictionary["whole_session_data"][
                            "press_a_width"] // settings.KEYPRESS_LOCATION_WIDTH_DIVISOR,
                        settings.SECOND_MONITOR_HEIGHT // settings.KEYPRESS_LOCATION_SECMON_HEIGHT_DIVISOR
                        - DataDictionary["whole_session_data"][
                            "press_a_height"] // settings.KEYPRESS_LOCATION_HEIGHT_DIVISOR,
                    )
                )
                pygame.display.flip()

                # Determine trial result and trial type based on stimulus
                if stimulus == "buzz":
                    trial_dictionary["result"] = "hit"
                    trial_data["trial_type"] = "hit"
                elif stimulus == "bear":
                    trial_dictionary["result"] = "false alarm"
                    trial_data["trial_type"] = "false alarm"
                break

        elapsed_time = time.time() - start_time
        if elapsed_time >= settings.RIFG_TRIAL_DURATION:
            # Handle cases where 'a' was not pressed within the trial duration
            trial_dictionary["pressed_a_num_of_times"] = pressed_a_counter
            if pressed_a_counter == 0:
                if stimulus == "buzz":
                    trial_dictionary["result"] = "miss"
                    trial_data["trial_type"] = "miss"
                elif stimulus == "bear":
                    trial_dictionary["result"] = "correct rejection"
                    trial_data["trial_type"] = "correct rejection"
            break

    # Append trial data to the event CSV
    create_event_csv(event_csv_path, trial_data)

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
DataDictionary ["current_onset"] = 0.0
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
    # Define the event CSV file path
    task_type = DataDictionary["whole_session_data"]["task_type"]
    event_csv_dir = settings.RIFG_EVENT_CSV_DIR  # Directory for the event CSV file
    os.makedirs(event_csv_dir, exist_ok=True)  # Ensure the directory exists

    # Build the event CSV file name
    participant_id = DataDictionary["whole_session_data"]["pid"]
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    session_num = DataDictionary["whole_session_data"].get("session_num", "01")

    event_csv_suffix = f"{task_type.lower()}RIFG_events.csv"
    event_csv_name = f"{participant_id}_rifg_task_session{session_num}_{timestamp}_{event_csv_suffix}"
    event_csv_path = os.path.join(event_csv_dir, event_csv_name)

    # Initialize onset time as a float
    onset_time = 0.0

    # Add the initial 30-second rest period
    initial_rest = {
        "onset": round(onset_time, 1),
        "duration": 30.0,
        "trial_type": "rest"
    }
    create_event_csv(event_csv_path, initial_rest)

    # Update onset for the first trial
    onset_time += 30.0
    DataDictionary["current_onset"] = onset_time

    # Run Each Trial
    for trial in range(1, settings.RIFG_N_TRIALS + 1):
        try:
            # Check for quit events
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    raise KeyboardInterrupt("Quit key pressed")

            Logger.print_and_log(f" ==== Starting Trial {trial} ==== ")

            # Make a sub-dictionary in the DataDictionary for this trial
            DataDictionary[f"trial{trial}"] = {}
            trial_dictionary = DataDictionary[f"trial{trial}"]

            # Show fixation cross
            Projector.show_fixation_cross(dictionary=DataDictionary, screen=screen)
            pygame.display.flip()

            # Sleep for the interstimulus interval
            Logger.print_and_log(f"Sleeping for interstimulus interval {ISI_list[trial - 1]}")
            time.sleep(ISI_list[trial - 1])

            # Define trial duration
            trial_duration = settings.RIFG_TRIAL_DURATION
            isi_duration = 1.0  # Fixed ISI duration

            # Run the trial and handle responses
            handle_trial(
                DataDictionary=DataDictionary,
                trial_number=trial,
                event_csv_path=event_csv_path
            )

            # Increment onset by trial duration and ISI
            onset_time += trial_duration + isi_duration
            DataDictionary ["current_onset"] = onset_time

        except KeyboardInterrupt:
            Logger.print_and_log("Quit Session.")
            break  # Exit the trial loop upon quit

    # Add the final 30-second rest period if the task was not interrupted
    final_rest = {
        "onset": round(onset_time, 1),  # Ensure one decimal place
        "duration": 30.0,
        "trial_type": "rest"
    }
    create_event_csv(event_csv_path, final_rest)

finally:
    if csv_log_path:
        # Update the existing CSV log file using the path created earlier
        Logger.update_log(log_name=csv_log_path, dictionary_to_write=DataDictionary)

        Projector.show_fixation_cross_rest(screen=screen, dictionary=DataDictionary, Get_CSV_if_Error=True)
        pygame.display.flip()

    # Ensure the task ends properly with an "ending_cause"
    if "ending_cause" not in DataDictionary['whole_session_data'] or DataDictionary['whole_session_data']['ending_cause'] != "keyboard_interrupt":
        DataDictionary['whole_session_data']["ending_cause"] = "undocumented or regular"

    if csv_log_path:
        # Update the same CSV log file again with the final state
        Logger.update_log(log_name=csv_log_path, dictionary_to_write=DataDictionary)

    # Show the end message
    Projector.show_end_message(screen=screen)

