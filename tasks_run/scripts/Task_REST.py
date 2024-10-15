import Projector
import settings


print("STARTING REST TASK...")
dictionary: dict = {"whole_session_data": {}}

# get monitor information and use to create the game window, record the information in the data dictionary
dictionary, screen = Projector.get_monitor_info(dictionary=dictionary)

# initialize the screen
Projector.initialize_screen(screen=screen, instructions=settings.REST_INSTRUCTIONS)

# show instructions and wait for 's' keypress
Projector.show_instructions(screen=screen, instructions=settings.REST_INSTRUCTIONS)

# show fixation cross for the rest task time given in settings.py
Projector.show_fixation_cross_rest(dictionary=dictionary, screen=screen, Get_CSV_if_Error=False, rest_task=True)

# show message after done
Projector.show_message(screen=screen, message=settings.REST_MESSAGE_AFTER_DONE, wait_for_scanner=False)