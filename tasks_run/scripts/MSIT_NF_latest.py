import random
import time
import Logger
import settings
import Projector
import pygame
from datetime import datetime
import ScriptManager

CONTROL_BLOCK = 333
INTERFERENCE_BLOCK = 444
TRIALS_PER_SESSION = 24
NUM_SESSIONS = 8
ISI = 1.75

def handle_response(trial_dictionary: dict, screen_width: float, screen_height: float, screen, feedback_font) -> dict:
    Response = None
    start_time = pygame.time.get_ticks()
    feedback_font = pygame.font.Font(None, settings.MSIT_FONT_SIZE_FEEDBACK)

    while Response is None:
        current_time = pygame.time.get_ticks()

        if current_time - start_time > 3000:  # 3 seconds timeout
            Logger.print_and_log("No Response For This Trial")
            # If no response, process the trial with the feedback display function
            trial_dictionary = check_response(trial_dictionary=trial_dictionary, screen=screen, screen_width=screen_width, screen_height=screen_height, feedback_font=feedback_font)
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                trial_dictionary["reaction_time"] = datetime.now() - trial_dictionary["start_time"]
                if event.key == pygame.K_a or event.key == pygame.K_1:
                    Logger.print_and_log("Response: A/1")
                    Response = 1
                    trial_dictionary["response"] = Response
                    trial_dictionary = check_response(trial_dictionary=trial_dictionary, feedback_font=feedback_font, screen=screen, screen_width=screen_width, screen_height=screen_height)
                elif event.key == pygame.K_b or event.key == pygame.K_2:
                    Logger.print_and_log("Response: B/2")
                    Response = 2
                    trial_dictionary["response"] = Response
                    trial_dictionary = check_response(trial_dictionary=trial_dictionary, feedback_font=feedback_font, screen=screen, screen_width=screen_width, screen_height=screen_height)
                elif event.key == pygame.K_c or event.key == pygame.K_3:
                    Logger.print_and_log("Response: C/3")
                    Response = 3
                    trial_dictionary["response"] = Response
                    trial_dictionary = check_response(trial_dictionary=trial_dictionary, feedback_font=feedback_font, screen=screen, screen_width=screen_width, screen_height=screen_height)

    return trial_dictionary

def check_response(trial_dictionary: dict, screen, feedback_font, screen_width: float, screen_height: float) -> dict:
    given_number_one: list = []
    given_number_two: list = []

    # Separate the numbers from the trial dictionary's number series
    for index, number in enumerate(trial_dictionary["number_series"], start=1):
        if index == 1:
            given_number_one.append(number)
        elif number == given_number_one[0]:
            given_number_one.append(number)
        else:
            given_number_two.append(number)

    # Determine the "different number" in the trial
    if len(given_number_one) == 1:
        trial_dictionary["different_number"] = given_number_one[0]
    elif len(given_number_two) == 1:
        trial_dictionary["different_number"] = given_number_two[0]
    else:
        raise ValueError("Math went wrong, check check_response()")

    # Log the different number and check correctness
    Logger.print_and_log(f"Different Number was: {trial_dictionary['different_number']}")
    if trial_dictionary["different_number"] == trial_dictionary["response"]:
        trial_dictionary["correct"] = True
        Logger.print_and_log("Participant was Correct.")
        feedback_text = "Correct"
        feedback_color = (0, 255, 0)  # Green for correct
    else:
        trial_dictionary["correct"] = False
        Logger.print_and_log("Participant was Incorrect.")
        feedback_text = "Incorrect"
        feedback_color = (255, 0, 0)  # Red for incorrect

    # Render feedback text on the screen above the numbers
    feedback_surface = feedback_font.render(feedback_text, True, feedback_color)
    feedback_rect = feedback_surface.get_rect(center=(screen_width // 2, (screen_height // 2) - 50))  # Positioned above the numbers

    # Show feedback on the screen
    screen.fill((0, 0, 0))  # Clear the screen
    screen.blit(feedback_surface, feedback_rect)  # Blit the feedback text

    # Delay to show feedback for a short time (e.g., 1 second)
    pygame.display.flip()
    pygame.time.delay(1000)

    return trial_dictionary
def generate_series(block_type: int) -> list:
    series_list: list = []

    if block_type == CONTROL_BLOCK:
        random.seed (1234) #set fixed seed for pseudorandom order in control block
    elif block_type == INTERFERENCE_BLOCK:
        random.seed (5678) #set fixed seed for pseudorandom order in interference block

    for i in range(10):
        series = [0,0,0]

        if block_type == CONTROL_BLOCK:
            target_number = random.randint(1, 3)
            positions = [0, 1, 2]
            random.shuffle(positions)
            series[positions[0]] = target_number

        elif block_type == INTERFERENCE_BLOCK:
            same_number = random.randint(1, 3)
            different_number = same_number
            while different_number == same_number:
                different_number = random.randint(1, 3)

            positions = [0, 1, 2]
            random.shuffle(positions)

            series: list = [same_number, same_number, same_number]
            series[positions[0]] = different_number

        series_list.append(series)

    return series_list

def run_msit_task():
    Data_Dictionary = {'whole_session_data': {}}

    pygame.init()
    number_font = pygame.font.Font(None, settings.MSIT_FONT_SIZE_NUMBERS)
    random.seed(settings.RANDOM_SEED_VALUE)

    Data_Dictionary, screen = Projector.get_monitor_info(dictionary=Data_Dictionary)
    screen_width = Data_Dictionary["whole_session_data"]["second_monitor_width"]
    screen_height = Data_Dictionary["whole_session_data"]["second_monitor_height"]

    Data_Dictionary["whole_session_data"]["pid"] = ScriptManager.get_participant_id()
    output_log_path = Logger.create_log(filetype=".txt",
                                        log_name=f"{Data_Dictionary['whole_session_data']['pid']}_MSIT")

    practice: str = ""
    while True:
        practice: str = input("Practice Block? (y/n): ")
        if practice == 'y':
            Logger.print_and_log("OK, Will Run This As a Practice Session.")
            practice: bool = True
            break
        elif practice == 'n':
            Logger.print_and_log("Ok. Not a Practice Session.")
            practice: bool = False
            break
        else:
            Logger.print_and_log("Please chose either 'y' or 'n'")

    block_type = ""
    while block_type not in ["I", "C"]:
        block_type = input("Block Type (I/C)?").upper()
        if block_type == "I":
            Logger.print_and_log("Interference Block Selected.")
            block_type = INTERFERENCE_BLOCK
            break
        elif block_type == "C":
            Logger.print_and_log("Control Block Selected.")
            block_type = CONTROL_BLOCK
            break
        else:
            Logger.print_and_log("Please choose either 'I' (Interference) or 'C' (Control)")

    Data_Dictionary["whole_session_data"]["block_type"] = block_type

    Projector.show_instructions(screen=screen, instructions=settings.MSIT_INSTRUCTIONS)

    Projector.show_fixation_cross_rest(screen=screen, dictionary=Data_Dictionary, Get_CSV_if_Error=True)

    # loop through the 8 sessions, alternating between control and interference blocks
    for session_num in range (NUM_SESSIONS):
        if session_num % 2 == 0:
            block_type = CONTROL_BLOCK
        else:
            block_type = INTERFERENCE_BLOCK

        Logger.print_and_log(f"Session {session_num +1}: Block Type = {'Control' if block_type == CONTROL_BLOCK else 'Interference'}")

        series_list = generate_series(block_type)

        for trial in range (1, TRIALS_PER_SESSION + 1):
            Logger.print_and_log(f"=======Trial {trial}=======")
            Data_Dictionary[f"trial{trial}"] = {}
            Data_Dictionary[f"trial{trial}"]["start_time"] = datetime.now()
            Data_Dictionary[f"trial{trial}"]["block_type"] = block_type

            # Display the numbers for this trial
            screen.fill((0, 0, 0))
            numbers_this_trial = series_list[trial - 1]
            Data_Dictionary[f"trial{trial}"]["number_series"] = numbers_this_trial

            numbers_text = f"{numbers_this_trial[0]}  {numbers_this_trial[1]}  {numbers_this_trial[2]}"
            text_surface = number_font.render(numbers_text, True, (255, 255, 255))

            center_x = int(screen_width // settings.MSIT_SCREEN_DIVISORS_FOR_NUMBERS[0])
            center_y = int(screen_height // settings.MSIT_SCREEN_DIVISORS_FOR_NUMBERS[1])

            text_rect = text_surface.get_rect(center=(center_x, center_y))
            screen.blit(text_surface, text_rect)
            pygame.display.flip()

            # Handle the response and feedback
            Data_Dictionary[f"trial{trial}"] = handle_response(trial_dictionary=Data_Dictionary[f"trial{trial}"], screen_width=screen_width
                                              , screen_height=screen_height, screen=screen, feedback_font=settings.MSIT_FONT_SIZE_FEEDBACK)

            # Mark the end time of the trial
            Data_Dictionary[f"trial{trial}"]["end_time"] = datetime.now()

            # Inter-Stimulus Interval (ISI)
            time.sleep(ISI)

            # After all sessions are done, log the results and finish
        csv_log_dir = Logger.create_log(filetype=".csv",
                                        log_name=f"{Data_Dictionary['whole_session_data']['pid']}_msit_data")
        Logger.update_log(log_name=csv_log_dir, dictionary_to_write=Data_Dictionary)
        Projector.show_fixation_cross_rest(screen=screen, dictionary=Data_Dictionary, Get_CSV_if_Error=True)
        Projector.show_end_message(screen=screen)

if __name__ == "__main__":
    run_msit_task()






