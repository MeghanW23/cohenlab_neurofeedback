import FileHandler
import pygame
import Projector
import settings
import Logger
import ScriptManager
import time

print("STARTING REST TASK...")

dictionary: dict = {"whole_session_data": {}}
pygame.init()

Logger.InterruptHandler.start_keyboard_listener() # start keyboard listener for esc key pressed

# textfiles required for many functions from the modules
pid =  FileHandler.validate_inputted_pid_is_new(ScriptManager.get_participant_id())
while True:
    session_number = input("Which rest session is this? (1, 2, 3, or 4): ").strip()
    if session_number in ["1", "2", "3", "4"]:
        print(f"Ok, running rest  {session_number}...")
        break
    else:
        print("Invalid input. Please enter 1, 2, 3, or 4.")

Logger.create_log(filetype=".txt", log_name=f"{pid}_rest{session_number}_log")

# get monitor information and use to create the game window, record the information in the data dictionary
dictionary, screen = Projector.get_monitor_info(dictionary=dictionary)

# write to vnc viewer log to open the vnc 
Logger.write_to_open_viewer_log()

# initialize the screen
Projector.initialize_screen(screen=screen, instructions=settings.REST_INSTRUCTIONS, dictionary=dictionary)

# show instructions and wait for 's' keypress
Projector.show_instructions(screen=screen, instructions=settings.REST_INSTRUCTIONS)

# show fixation cross for the rest task time given in settings.py
Projector.show_fixation_cross_rest(screen=screen, rest_task=True)

# show message after done
Projector.show_message(screen=screen, message=settings.REST_MESSAGE_AFTER_DONE, wait_for_scanner=False)

print("Rest is Done. Exiting automatically in 5 seconds...")
time.sleep(5)