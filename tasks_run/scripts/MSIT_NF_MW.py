import random
import time

import ScriptManager
import Logger
import settings
import Projector
import pygame
from datetime import datetime, timedelta
import pprint
def generate_series() -> list:
    series_list: list = []

    for i in range(10):
        same_number: int = random.randint(0, 2)

        different_number: int = same_number
        while different_number == same_number:
            different_number: int = random.randint(0, 2)

        positions: list = [0, 1, 2]  # Positions 0, 1, and 2
        random.shuffle(positions)  # Shuffle positions to decide where the different number will go

        series: list = [same_number, same_number, same_number]
        series[positions[0]] = different_number  # Assign different number to random position

        series_list.append(series)

    return series_list

def handle_response(trial_dictionary: dict, screen_width: float, screen_height: float) -> dict:
    Response = None
    start_time = pygame.time.get_ticks()

    while Response is None:
        current_time = pygame.time.get_ticks()

        # Timeout after 3 seconds
        if current_time - start_time > 3000:
            Logger.print_and_log("No Response For This Trial")
            trial_dictionary["response"] = Response
            trial_dictionary = check_response(trial_dictionary=Data_Dictionary[f"trial{trial}"])
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # Key presses mapped to positions
            if event.type == pygame.KEYDOWN:
                trial_dictionary["reaction_time"] = datetime.now() - trial_dictionary["start_time"]
                if event.key == pygame.K_a or event.key == pygame.K_0:  # 'A' key is position 0
                    Logger.print_and_log("Response: A/0")
                    Response = 0
                    trial_dictionary["response"] = Response
                    trial_dictionary = check_response(trial_dictionary=Data_Dictionary[f"trial{trial}"])
                    if practice:
                        show_feedback(trial_dictionary=trial_dictionary, screen_width=screen_width, screen_height=screen_height)

                elif event.key == pygame.K_b or event.key == pygame.K_1:  # 'B' key is position 1
                    Logger.print_and_log("Response: B/1")
                    Response = 1
                    trial_dictionary["response"] = Response
                    trial_dictionary = check_response(trial_dictionary=Data_Dictionary[f"trial{trial}"])
                    if practice:
                        show_feedback(trial_dictionary=trial_dictionary, screen_width=screen_width, screen_height=screen_height)

                elif event.key == pygame.K_c or event.key == pygame.K_2:  # 'C' key is position 2
                    Logger.print_and_log("Response: C/2")
                    Response = 2
                    trial_dictionary["response"] = Response
                    trial_dictionary = check_response(trial_dictionary=Data_Dictionary[f"trial{trial}"])
                    if practice:
                        show_feedback(trial_dictionary=trial_dictionary, screen_width=screen_width, screen_height=screen_height)

    return trial_dictionary

def check_response(trial_dictionary: dict) -> dict:
    given_number_one: list = []
    given_number_two: list = []
    for index, number in enumerate(trial_dictionary["number_series"], start=1):
        if index == 1:
            given_number_one.append(number)
        elif number == given_number_one[0]:
            given_number_one.append(number)
        else:
            given_number_two.append(number)
        
    if len(given_number_one) == 1:
        trial_dictionary["different_number"] = given_number_one[0]
    elif len(given_number_two) == 1:
        trial_dictionary["different_number"] = given_number_two[0]
    else:
        raise ValueError("Math went wrong, check check_response()")

    Logger.print_and_log(f"Different Number was: {trial_dictionary['different_number']}")
    if trial_dictionary["different_number"] == trial_dictionary["response"]:
        trial_dictionary["correct"]: bool = True
        Logger.print_and_log("Participant was Correct.")
    else:
        trial_dictionary["correct"]: bool = False
        Logger.print_and_log("Participant was Incorrect.")


    return trial_dictionary

def show_feedback(trial_dictionary, screen_width, screen_height):
    if trial_dictionary["correct"]:
        feedback: str = "correct"
        color: tuple = (0, 255, 0)
    else:
        feedback: str = "incorrect"
        color: tuple = (255, 0, 0)


    feedback_text_surface = feedback_font.render(feedback, True, color)
    feedback_text_rect: pygame.Rect = feedback_text_surface.get_rect(center=(screen_width // settings.MSIT_SCREEN_DIVISORS_FOR_FEEDBACK[0], screen_height // settings.MSIT_SCREEN_DIVISORS_FOR_FEEDBACK[1]))
    screen.blit(feedback_text_surface, feedback_text_rect)
    pygame.display.flip()


    time.sleep(settings.MSIT_TIME_TO_SHOW_FEEDBACK)

Data_Dictionary: dict = {'whole_session_data': {}}

pygame.init()
number_font = pygame.font.Font(None, settings.MSIT_FONT_SIZE_NUMBERS)
feedback_font = pygame.font.Font(None, settings.MSIT_FONT_SIZE_FEEDBACK)
random.seed(settings.RANDOM_SEED_VALUE)

# set a fixed seed for reproducibility of a pseudorandom series
random.seed(settings.RANDOM_SEED_VALUE)
Data_Dictionary["whole_session_data"]["pid"] = ScriptManager.get_participant_id()
output_log_path = Logger.create_log(filetype=".txt", log_name=f"{Data_Dictionary['whole_session_data']['pid']}_MSIT")
# Logger.print_and_log(f"Created Text Output File: {output_log_path}")

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

Data_Dictionary, screen = Projector.get_monitor_info(dictionary=Data_Dictionary)
Projector.initialize_screen(screen=screen, instructions=settings.MSIT_INSTRUCTIONS)
Projector.show_instructions(screen=screen, instructions=settings.MSIT_INSTRUCTIONS)
Projector.show_fixation_cross_rest(dictionary=Data_Dictionary, screen=screen, Get_CSV_if_Error=True)

series_list: list = generate_series()
for trial in range(1, settings.MSIT_N_TRIALS + 1):
    Logger.print_and_log(f"=======Trial{trial}=======")
    Data_Dictionary[f"trial{trial}"]: dict = {}
    Data_Dictionary[f"trial{trial}"]["start_time"] = datetime.now()
    screen.fill((0, 0, 0))

    numbers_this_trial: list = random.choice(series_list)
    Data_Dictionary[f"trial{trial}"]["number_series"]: list = numbers_this_trial
    
    numbers_text = f"{numbers_this_trial[0]}  {numbers_this_trial[1]}  {numbers_this_trial[2]}"
    text_surface = number_font.render(numbers_text, True, (255, 255, 255))
    screen_width: float = Data_Dictionary["whole_session_data"]["second_monitor_width"]
    screen_height: float = Data_Dictionary["whole_session_data"]["second_monitor_height"]

    text_rect: pygame.Rect = text_surface.get_rect(center=(screen_width // settings.MSIT_SCREEN_DIVISORS_FOR_NUMBERS[0],  screen_height // settings.MSIT_SCREEN_DIVISORS_FOR_NUMBERS[1]))

    screen.blit(text_surface, text_rect)
    pygame.display.flip()

    Data_Dictionary[f"trial{trial}"] = handle_response(trial_dictionary=Data_Dictionary[f"trial{trial}"], screen_width=screen_width, screen_height=screen_height)

    Data_Dictionary[f"trial{trial}"]["end_time"] = datetime.now()

csv_log_dir = Logger.create_log(filetype=".csv", log_name=f"{Data_Dictionary['whole_session_data']['pid']}_msit_data")
Logger.update_log(log_name=csv_log_dir, dictionary_to_write=Data_Dictionary)
Projector.show_end_message(screen=screen)