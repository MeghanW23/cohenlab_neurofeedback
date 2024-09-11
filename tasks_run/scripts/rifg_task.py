import pygame
import random
import os
import time
from datetime import datetime
import csv
from typing import Tuple
import settings
pygame.init()  # initialize Pygame
print("This Task is a Stop Task Aimed at activating the rIFG and ACC.")

""" PATHS """
buzz: pygame.Surface = pygame.image.load(settings.BUZZ_PATH)
alien: pygame.Surface = pygame.image.load(settings.ALIEN_PATH)
fixation: pygame.Surface = pygame.image.load(settings.FIXATION_PATH)
pressed_a: pygame.Surface = pygame.image.load(settings.PRESSED_A_PATH)
default_output_log_directory: str = settings.RIFG_OUTDIR

random.seed(settings.RANDOM_SEED_VALUE)

""" FUNCTIONS """
def print_data_dictionary(dictionary: dict, dictionary_name: str = None) -> None:
    """
    Prints a dictionary to the terminal in a more readable way, with special formatting for sub-dictionaries.

    Args:
        dictionary (dict): The dictionary to be printed.
        dictionary_name (str, optional): A name to identify the dictionary in the output.
                                         If provided, it will be printed before the dictionary content.

    Returns:
        None
    """
    if dictionary_name is not None:
        print("\n---")
        print(f"Printing Info on {dictionary_name} Below: ")
    else:
        print(f"Printing Dictionary Information Below: \n")

    for key, value in dictionary.items():
        print("---")

        if isinstance(dictionary[key], dict): # if this key in the dictionary is a subdictionary, format a different way
            print(f"dictionary: {key}")
            for subkey, subvalue in dictionary[key].items():
                print(f"  {subkey}: {subvalue}")
        else:
            print(f"key: {key}, value: {value}")

    print("---\n")

def get_monitor_info(dictionary: dict) -> Tuple[dict, pygame.Surface]:
    # Set up display
    screen_info: pygame.display.Info = pygame.display.Info()
    SCREEN_WIDTH: int = screen_info.current_w
    SCREEN_HEIGHT: int = screen_info.current_h
    print(f"experimenter screen width: {SCREEN_WIDTH}")
    print(f"experimenter screen height: {SCREEN_HEIGHT}")

    dictionary["whole_session_data"]["experimenter_screen_width"]: int = SCREEN_WIDTH
    dictionary["whole_session_data"]["experimenter_screen_height"]: int = SCREEN_HEIGHT
    dictionary["whole_session_data"]["second_monitor_width"]: int = settings.SECOND_MONITOR_WIDTH
    dictionary["whole_session_data"]["second_monitor_height"]: int = settings.SECOND_MONITOR_HEIGHT
    dictionary["whole_session_data"]["monitor_X_OFFSET"]: int = settings.MONITOR_X_OFFSET
    dictionary["whole_session_data"]["monitor_Y_OFFSET"]: int = settings.MONITOR_Y_OFFSET

    print(f"Second monitor resolution: {settings.SECOND_MONITOR_WIDTH}x{settings.SECOND_MONITOR_HEIGHT}")

    # Set the display position (offset from the primary display)
    os.environ['SDL_VIDEO_WINDOW_POS'] = f'{settings.MONITOR_X_OFFSET},{settings.MONITOR_Y_OFFSET}'

    # Create a Pygame display window on the second monitor
    screen = pygame.display.set_mode((DataDictionary["whole_session_data"]["second_monitor_width"], DataDictionary["whole_session_data"]["second_monitor_height"]), pygame.FULLSCREEN | pygame.NOFRAME)

    return dictionary, screen
def get_participant_id() -> str:
    """
    Prompts the user to input a participant ID (PID) and validates the input against specific criteria.

    The function ensures that the PID starts with the letter 'p' or 'P' and is followed by numeric characters only.
    It repeatedly prompts the user until a valid PID is entered.

    Returns:
        str: A valid participant ID that starts with 'p' or 'P' followed by numeric characters.

    Example:
        When prompted, if the user enters an invalid PID (e.g., "x123" or "p12a"), the function will print
        an error message and ask for the PID again. If the user enters a valid PID (e.g., "p1234"), the
        function will accept it and return "p1234".
    """
    acceptable_characters: list = ["p", "P", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    while True:
        Retrying: bool = False
        pid: str = input("Enter PID: ")

        if not pid.startswith("p") and not pid.startswith("P"):
            print("Please Assure Your Inputted PID starts with 'P' or 'p'")
            Retrying: bool = True

        if len(pid) == 1:
            print("Please Assure Your PID Follows Syntax: the letter 'p' followed by numbers only.")
            Retrying: bool = True

        for character in pid:
            iterator: int = 0
            if character not in acceptable_characters:
                if iterator == 0:  # only print out this line once (not for every unacceptable character)
                    print("Please Assure Your PID Follows Syntax: the letter 'p' followed by numbers only.")
                iterator += 1
                Retrying: bool = True

        if not Retrying:
            print(f"OK, Using PID: {pid}")
            break

    return pid

def handle_trial(DataDictionary: dict, trial_number: int) -> dict:
    """
    Handles the execution and data recording for a single trial.

    This function retrieves the trial-specific dictionary from a main data dictionary, initiates the trial by
    selecting a random stimulus, and records various parameters such as reaction time and trial results.
    The trial involves displaying a stimulus and recording user responses (e.g., pressing the 'a' key).

    Args:
        DataDictionary (dict): The main dictionary containing all trial data and session-wide configurations.
        trial_number (int): The current trial number, used to retrieve the specific trial dictionary.

    Returns:
        dict: The updated trial dictionary containing recorded data like trial type, start time,
              reaction time, and result.

    Example:
        During a trial, the function will:
        1. Select a random stimulus from a predefined list.
        2. Record the time the trial started.
        3. Monitor for the participant pressing the 'a' key.
        4. If 'a' is pressed, calculate and record the reaction time.
        5. Display a response message on the screen based on the stimulus type.
        6. Determine and record the trial result as either "hit" or "false alarm" based on the stimulus.

    The function assumes that the environment is set up with Pygame and that the `blit_trial` and other necessary
    variables and functions are correctly defined.
    """
    trial_dictionary: dict = DataDictionary[f"trial{trial_number}"]  # pull this trial's dictionary from main dictionary
    pressed_a_counter: int = 0  # count times 'a' is pressed

    start_time: float = time.time()  # Record the start time

    conditions_list: list = ["buzz", "buzz", "buzz", "alien"]  # Participants have a 75% chance of getting Buzz
    random.shuffle(conditions_list)
    stimulus: str = random.choice(conditions_list)  # chose random condition from conditions_list
    print(f"trial_type:{stimulus}")

    # record info on trial to dictionary
    trial_dictionary["trial_type"]: str = stimulus
    trial_dictionary["start_time"]: float = start_time

    while True:
        blit_trial(stimulus=stimulus)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                print("Pressed A")

                pressed_a_counter += 1

                if pressed_a_counter == 1:
                    # get reaction time
                    current_time: float = time.time()  # Get the current time
                    elapsed_time: float = current_time - start_time  # Calculate elapsed time
                    trial_dictionary["time_to_first_a_press"]: float = elapsed_time

                # pull screen information from data dictionary
                press_a_width: int = DataDictionary["whole_session_data"]["press_a_width"]
                press_a_height: int = DataDictionary["whole_session_data"]["press_a_height"]

                # show "pressed 'a'" image if 'a' is pressed
                screen.blit(pressed_a_resized, (settings.SECOND_MONITOR_WIDTH // settings.KEYPRESS_LOCATION_SECMON_WIDTH_DIVISOR - press_a_width // settings.KEYPRESS_LOCATION_WIDTH_DIVISOR, settings.SECOND_MONITOR_HEIGHT // settings.KEYPRESS_LOCATION_SECMON_HEIGHT_DIVISOR - press_a_height // settings.KEYPRESS_LOCATION_HEIGHT_DIVISOR))  # report keypress 'a'

                pygame.display.flip()

                # record trial results if 'a' was pressed
                if stimulus == "buzz":
                    trial_dictionary["result"]: str = "hit"

                elif stimulus == "alien":
                    trial_dictionary["result"]: str = "false alarm"

                break

        current_time: float = time.time()  # Get the current time
        elapsed_time: float = current_time - start_time  # Calculate elapsed time
        if elapsed_time >= 1:  # Check if a second has passed
            # record trial results if a wasn't ever pressed in the 1 second time limit
            trial_dictionary["pressed_a_num_of_times"]: int = pressed_a_counter
            if pressed_a_counter == 0:
                if stimulus == "buzz":
                    trial_dictionary["result"]: str = "miss"
                elif stimulus == "alien":
                    trial_dictionary["result"]: str = "correct rejection"

            print("A second has passed.")
            trial_dictionary["full_second_has_passed"] = True
            break

    return DataDictionary

def blit_trial(stimulus):
    """
    Displays a specific stimulus on the screen based on the trial's stimulus type.

    Depending on whether the stimulus is "buzz" or "alien," this function blits (renders)
    the corresponding image onto the screen at a specified position. The function handles
    the display update and positioning based on the screen dimensions provided in the
    `DataDictionary`.

    Args:
        stimulus (str): The type of stimulus to display. It should be either "buzz" or "alien".

    Returns:
        None

    Example:
        If the stimulus is "buzz", the function will:
        1. Retrieve the dimensions for the buzz image from `DataDictionary`.
        2. Calculate the position to center the buzz image on the screen.
        3. Render the buzz image at the calculated position and update the display.

        Similarly, if the stimulus is "alien", the function will perform the same steps
        but for the alien image.

    The function assumes that the Pygame environment is properly initialized and that
    the `screen`, `buzz_resized`, and `alien_resized` variables are defined and contain
    the images to be displayed.
    """
    # blit image using information on image sizes from data dictionary
    if stimulus == "buzz":
        buzz_width: int = DataDictionary["whole_session_data"]["buzz_width"]
        buzz_height: int = DataDictionary["whole_session_data"]["buzz_height"]
        screen.blit(buzz_resized, (settings.SECOND_MONITOR_WIDTH // settings.BUZZ_ALIEN_LOCATION_SECMON_WIDTH_DIVISOR - buzz_width // settings.BUZZ_ALIEN_LOCATION_WIDTH_DIVISOR, settings.SECOND_MONITOR_HEIGHT // settings.BUZZ_ALIEN_LOCATION_SECMON_HEIGHT_DIVISOR - buzz_height // settings.BUZZ_ALIEN_LOCATION_HEIGHT_DIVISOR))

        pygame.display.flip()
    else:
        alien_width: int = DataDictionary["whole_session_data"]["alien_width"]
        alien_height: int = DataDictionary["whole_session_data"]["alien_height"]
        screen.blit(alien_resized, (settings.SECOND_MONITOR_WIDTH // settings.BUZZ_ALIEN_LOCATION_SECMON_WIDTH_DIVISOR - alien_width // settings.BUZZ_ALIEN_LOCATION_WIDTH_DIVISOR, settings.SECOND_MONITOR_HEIGHT // settings.BUZZ_ALIEN_LOCATION_SECMON_HEIGHT_DIVISOR - alien_height // settings.BUZZ_ALIEN_LOCATION_HEIGHT_DIVISOR))

        pygame.display.flip()

    return None

def show_instructions(DataDictionary: dict) -> None:
    """
    Displays instructions to participants on the screen and waits for the scanner to send a start signal.

    This function renders a series of instructions on the screen, guiding participants on how to perform the task.
    After displaying the instructions, it waits for the 's' key signal from the scanner to start the task.

    Args:
        DataDictionary (dict): A dictionary containing session-wide data, including screen dimensions.

    Returns:
        None

    Example:
        The function will:
        1. Display instructions like "Welcome to the Task!" and "Press 'A' using your left thumb when you see Buzz."
        2. Wait until the scanner sends the 's' key signal, indicating that the task should begin.

    The function assumes that the Pygame environment is properly initialized and that the `screen` variable is defined.
    """
    """
       # Calculate the total height needed for all instructions to be centered
    line_height = font.get_linesize()
    total_text_height = line_height * len(instructions)

    # Calculate the initial settings.INSTRUCT_Y_OFFSET to vertically center the text block
    settings.INSTRUCT_Y_OFFSET = (settings.SECOND_MONITOR_HEIGHT - total_text_height) // 2
    """

    font: pygame.font.Font = pygame.font.Font(None, settings.INSTRUCT_MESSAGE_FONT_SIZE)
    instructions: list = [
        "Welcome to the Task!",
        "Press 'A' using your left thumb when you see Buzz (the astronaut).",
        "Do NOT press anything when you see Alien.",
        "Ready..",
        "Set",
        "Go!"
    ]

    # Render and display each line of instructions
    screen.fill((0, 0, 0))

    for line in instructions:
        text: pygame.Surface = font.render(line, True, settings.FONT_COLOR)  # White text
        text_rect: pygame.Rect = text.get_rect(center=(settings.SECOND_MONITOR_WIDTH // settings.INSTRUCT_TEXT_RECT_SECMON_WIDTH_DIVISOR, settings.INSTRUCT_Y_OFFSET))
        screen.blit(text, text_rect)
        settings.INSTRUCT_Y_OFFSET += settings.INSTRUCT_Y_OFFSET_INCREMENT  # Increment y-position for each new line
        # settings.INSTRUCT_Y_OFFSET += line_height

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                return None
            else:
                time.sleep(0.1)

# Ensure you define this default directory or set it where needed
def save_to_log_file(dictionary: dict = None, create_log_file: bool = False, pid: str = None, output_log_directory: str = default_output_log_directory, output_log_path: str = None,  # Adding output_log_path to function parameters
trial: int = None):
    """
    Saves a dictionary of data to a log file. The function either creates a new log file or appends data
    to an existing one.

    Parameters:
    -----------
    dictionary : dict, optional
        A dictionary of data to save to the log file. The keys and values are written as rows in the CSV file.
    create_log_file : bool, optional
        If True, a new log file will be created. Otherwise, data will be appended to an existing log file.
    pid : str, optional
        The participant ID used to name the log file if a new one is created.
    output_log_directory : str, optional
        The directory where the log file will be saved. Defaults to 'default_output_log_directory'.
    output_log_path : str, optional
        The path to the existing log file where data will be appended. Must be provided if `create_log_file` is False.
    trial : int, optional
        The current trial number, if relevant. This will be recorded as a separator before appending the data.

    Returns:
    --------
    output_log_path : str
        The path to the log file (whether newly created or existing).

    Raises:
    -------
    ValueError
        If `output_log_path` is not provided and `create_log_file` is False.

    Example:
    --------
    save_to_log_file(dictionary={'ReactionTime': 0.5, 'Accuracy': 1},
                     create_log_file=True, pid='001', output_log_directory='/logs')
    """

    # Check if an output_log_path is provided or needs to be created
    if create_log_file:
        now: datetime = datetime.now()
        timestamp: str = now.strftime("%Y%m%d_%Hh%Mm%Ss")
        output_dir_filename: str = f"{pid}_{timestamp}_rifg_task_log.csv"
        output_log_path: str = os.path.join(output_log_directory, output_dir_filename)

        with open(output_log_path, 'w', newline='') as file:
            writer: csv.writer = csv.writer(file)
            writer.writerow(["Created Output Log File for", pid, "at", timestamp])

        print(f"Created Log File. Find At: {output_log_path}")

        return output_log_path

    # Ensure output_log_path is set if not creating a new log file
    if output_log_path is None:
        raise ValueError("output_log_path must be provided if not creating a new log file.")

    # Append data to an existing log file
    with open(output_log_path, 'a', newline='') as file:
        writer: csv.writer = csv.writer(file)
        if trial is not None:
            writer.writerow([f"====== Trial: {trial} ======"])
        for key, value in dictionary.items():
            writer.writerow([key, value])

def show_end_message():
    """
    Displays a message on the second monitor indicating the completion of the task.

    This function retrieves the width and height of the second monitor from the `DataDictionary` dictionary.
    It then uses Pygame to render a centered message in white text on a black background.
    The message displayed is: "You have now completed the task. Thank you for participating!".
    After rendering the message, it updates the display to show the message for 5 seconds before proceeding.

    The function assumes that the Pygame `screen` object and `DataDictionary` are already defined and accessible in the context where this function is called.

    Example:
        show_end_message()

    """
    print(f"SUBJECT IS DONE. DISPLAYING EXIT MESSAGE FOR {settings.DISPLAY_EXIT_MESSAGE_TIME}")

    font: pygame.font.Font = pygame.font.Font(None, settings.EXIT_MESSAGE_FONT_SIZE)
    ending_message: str = "You have now completed the task. Thank you for participating!"
    text: pygame.Surface = font.render(ending_message, True, settings.FONT_COLOR)  # White text
    text_rect: pygame.Rect = text.get_rect(center=(settings.SECOND_MONITOR_WIDTH // settings.INSTRUCT_TEXT_RECT_SECMON_WIDTH_DIVISOR, settings.SECOND_MONITOR_HEIGHT // settings.INSTRUCT_TEXT_RECT_SECMON_HEIGHT_DIVISOR))  # Centered text

    screen.fill((0, 0, 0))
    screen.blit(text, text_rect)

    pygame.display.flip()

    time.sleep(settings.DISPLAY_EXIT_MESSAGE_TIME)  # show the message on screen for 5 seconds

""" SETUP """

# Create Dictionary to pull all needed data in, then Update Data Dictionary with the Experimental Parameters
DataDictionary: dict = {"whole_session_data": {
    'n_trials': settings.RIFG_N_TRIALS,
    'ISI_min': settings.ISI_MIN,
    'ISI_max': settings.ISI_MAX,
    'ISI_step': settings.ISI_STEP
}}

pid: str = get_participant_id()  # get participant ID by asking experimenter to input it via command line

DataDictionary["whole_session_data"]["pid"]: str = pid  # add participant id to whole session data dictionary

DataDictionary, screen = get_monitor_info(dictionary=DataDictionary)

# Resize Loaded Pygame images
new_width_buzz: int = settings.SECOND_MONITOR_WIDTH // settings.BUZZ_WIDTH_DIVISOR  # Desired width for buzz
new_height_buzz: int = settings.SECOND_MONITOR_HEIGHT // settings.BUZZ_HEIGHT_DIVISOR  # Desired height for buzz
buzz_resized: pygame.Surface = pygame.transform.scale(buzz, (new_width_buzz, new_height_buzz))
buzz_width: int = buzz_resized.get_width()
buzz_height: int = buzz_resized.get_height()
DataDictionary["whole_session_data"]["buzz_width"]: int = buzz_width
DataDictionary["whole_session_data"]["buzz_height"]: int = buzz_height


new_width_alien: int = settings.SECOND_MONITOR_WIDTH // settings.ALIEN_WIDTH_DIVISOR
new_height_alien: int = settings.SECOND_MONITOR_HEIGHT // settings.ALIEN_HEIGHT_DIVISOR
alien_resized: pygame.Surface = pygame.transform.scale(alien, (new_width_alien, new_height_alien))
alien_width: int = alien_resized.get_width()
alien_height: int = alien_resized.get_height()
DataDictionary["whole_session_data"]["alien_width"]: int = alien_width
DataDictionary["whole_session_data"]["alien_height"]: int = alien_height


new_width_fixation: int = settings.FIXATION_WIDTH
new_height_fixation: int = settings.FIXATION_HEIGHT
fix_resized: pygame.Surface = pygame.transform.scale(fixation, (new_width_fixation, new_height_fixation))
fixation_width: int = fix_resized.get_width()
fixation_height: int = fix_resized.get_height()
DataDictionary["whole_session_data"]["fixation_width"]: int = fixation_width
DataDictionary["whole_session_data"]["fixation_height"]: int = fixation_height

new_width_keypress: int = settings.KEYPRESS_WIDTH
new_height_keypress: int = settings.KEYPRESS_HEIGHT
pressed_a_resized: pygame.Surface = pygame.transform.scale(pressed_a, (new_width_keypress, new_height_keypress))
press_a_width: int = pressed_a_resized.get_width()
press_a_height: int = pressed_a_resized.get_height()
DataDictionary["whole_session_data"]["press_a_width"]: int = press_a_width
DataDictionary["whole_session_data"]["press_a_height"]: int = press_a_height

print_data_dictionary(DataDictionary, dictionary_name="All Session Data")  # print session data to terminal

output_log_path = save_to_log_file(create_log_file=True, pid=pid)  # create log file
save_to_log_file(dictionary=DataDictionary["whole_session_data"], output_log_path=output_log_path)
show_instructions(DataDictionary=DataDictionary)  # Show Instructions

# Run Each Trial
for trial in range(1, settings.RIFG_N_TRIALS + 1):
    print(f" ==== Starting Trial {trial} ==== ")

    # make a sub-dictionary in the data dictionary for this trial
    DataDictionary[f"trial{trial}"]: dict = {}
    trial_dictionary = DataDictionary[f"trial{trial}"]

    screen.fill((0, 0, 0))  # fill the screen black

    screen.blit(fix_resized, (settings.SECOND_MONITOR_WIDTH // settings.FIX_LOCATION_SECMON_WIDTH_DIVISOR -
                              fixation_width // settings.FIX_LOCATION_WIDTH_DIVISOR, settings.SECOND_MONITOR_HEIGHT // settings.FIX_LOCATION_SECMON_HEIGHT_DIVISOR -
                              fixation_height // settings.FIX_LOCATION_WIDTH_DIVISOR))  # show fixation cross

    pygame.display.flip()  # flip to monitor

    ISI: int = random.randrange(start=settings.ISI_MIN, stop=settings.ISI_MAX, step=settings.ISI_STEP)  # get random inter stimulus interval (in ms)
    print(f"ISI: {ISI}")
    trial_dictionary["ISI"] = ISI  # add ISI to trial_dictionary

    time.sleep(ISI / 1000.0)  # do the ISI wait time

    DataDictionary = handle_trial(DataDictionary=DataDictionary, trial_number=trial)   # Run the Buzz/Alien Part of Trial

    print_data_dictionary(trial_dictionary)  # print the data to the terminal

    save_to_log_file(dictionary=trial_dictionary, output_log_path=output_log_path, trial=trial) # save trial information to the log

show_end_message()

