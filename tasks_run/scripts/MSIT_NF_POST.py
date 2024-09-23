import Logger
import Projector
import pygame
from datetime import datetime
import ScriptManager
import sys
import time
import random
import settings


sys.path.append('/workdir/old_material/nf_projector.py')

# This is an MSIT Task built with Pygame that uses a random fixed seed to create a pesudorandom order for each block type, whether control or interference. This script has calls for the seeds to be presented POST task.


""" FUNCTIONS """
def handle_response(trial_dictionary: dict, screen_width: float, screen_height: float, screen, feedback_font) -> dict:
    Response = None
    start_time = pygame.time.get_ticks()
    feedback_font = pygame.font.Font(None, settings.MSIT_FONT_SIZE_FEEDBACK)

    while Response is None:
        current_time = pygame.time.get_ticks()

        # Check if 1.75 seconds have passed
        if current_time - start_time > settings.ISI * 1000:
            if trial_dictionary.get("response") is None:
                Logger.print_and_log("No Response For This Trial")
                trial_dictionary["reaction_time"] = None
                Logger.print_and_log(
                    f"Trial {trial_dictionary['trial_number']} - Block: {'Control' if trial_dictionary['block_type'] == settings.CONTROL_BLOCK else 'Interference'}")
                Logger.print_and_log(f"Number Series: {trial_dictionary['number_series']}")
                Logger.print_and_log("No Response Recorded")
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                reaction_time = (current_time - start_time) / 1000  # reaction time in seconds
                trial_dictionary["reaction_time"] = reaction_time
                trial_dictionary["response_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

                if event.key == pygame.K_a or event.key == pygame.K_1:
                    Logger.print_and_log("Response: A/1")
                    Response = 1
                elif event.key == pygame.K_b or event.key == pygame.K_2:
                    Logger.print_and_log("Response: B/2")
                    Response = 2
                elif event.key == pygame.K_c or event.key == pygame.K_3:
                    Logger.print_and_log("Response: C/3")
                    Response = 3

                trial_dictionary["response"] = Response
                trial_dictionary = check_response(trial_dictionary=trial_dictionary, screen=screen, feedback_font=feedback_font, screen_width=screen_width, screen_height=screen_height)
                break

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

    Logger.print_and_log(f"Trial {trial_dictionary['trial_number']} - Block: {'Control' if trial_dictionary['block_type'] == settings.CONTROL_BLOCK else 'Interference'}")
    Logger.print_and_log(f"Number Series: {trial_dictionary['number_series']}")
    Logger.print_and_log(f"Different Number: {trial_dictionary['different_number']}")
    Logger.print_and_log(f"Reaction Time: {trial_dictionary['reaction_time']}")

    feedback_text = ""
    feedback_color = None

    if trial_dictionary.get("response") is not None:
        if trial_dictionary["different_number"] == trial_dictionary["response"]:
            trial_dictionary["correct"] = True
            feedback_text = "Correct"
            feedback_color = (0, 255, 0)
            Logger.print_and_log("Response: Correct")
        else:
            trial_dictionary["correct"] = False
            feedback_text = "Incorrect"
            feedback_color = (255, 0, 0)
            Logger.print_and_log("Response: Incorrect")

        response_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        trial_dictionary["response_time"] = response_time
        Logger.print_and_log(f"Time of Response: {response_time}")

    else:
        trial_dictionary["correct"] = False
        feedback_text = "No Response"
        feedback_color = (255, 0, 0)
        Logger.print_and_log("No Response Given")

    # Render feedback text above the number series
    if feedback_text:
        feedback_surface = feedback_font.render(feedback_text, True, feedback_color)
        feedback_rect = feedback_surface.get_rect(center=(screen_width // 2, (screen_height // 2) - 100))

        # Blit the feedback text
        screen.blit(feedback_surface, feedback_rect)
        pygame.display.flip()

    return trial_dictionary

def generate_series(block_type: int, seed: int) -> list:
    series_list: list = []
    random.seed(seed)

    response_counts = {1:0, 2:0, 3:0}

    for i in range(settings.TRIALS_PER_SESSION):
        series = [0, 0, 0]
        positions = [0,1,2]

        if block_type == settings.CONTROL_BLOCK:
            possible_targets = [n for n in [1, 2, 3] if response_counts[n]<9]
            target_number = random.choice (possible_targets)
            response_counts[target_number] += 1

            random.shuffle (positions)
            series[positions[0]] = target_number

        elif block_type == settings.INTERFERENCE_BLOCK:
            same_number = random.choice([n for n in [1, 2, 3] if response_counts[n]<9])
            different_number = same_number
            while different_number == same_number:
                different_number = random.randint(1, 3)

            random.shuffle(positions)
            series = [same_number, same_number, same_number]
            series[positions[0]] = different_number
            response_counts[different_number] += 1

        # Ensure no consecutive duplicates
        if len(series_list) > 0 and series == series_list[-1]:
            while series == series_list[-1]:
                if block_type == settings.CONTROL_BLOCK:
                    possible_targets = [n for n in [1, 2, 3] if response_counts[n]<9]
                    target_number = random.choice(possible_targets)
                    random.shuffle(positions)
                    series = [0, 0, 0]
                    series[positions[0]] = target_number
                elif block_type == settings.INTERFERENCE_BLOCK:
                    same_number = random.choice([n for n in [1, 2, 3] if response_counts [n] < 9])
                    different_number = same_number
                    while different_number == same_number:
                        different_number = random.randint(1, 3)
                    random.shuffle(positions)
                    series = [same_number, same_number, same_number]
                    series[positions[0]] = different_number

        series_list.append(series)

    return series_list

def run_msit_task():
    Data_Dictionary = {'whole_session_data': {}}

    pygame.init()
    number_font = pygame.font.Font(None, settings.MSIT_FONT_SIZE_NUMBERS)
    random.seed(settings.RANDOM_SEED_VALUE)

    try:
        Data_Dictionary, screen = Projector.get_monitor_info(dictionary=Data_Dictionary)
        screen_width = Data_Dictionary["whole_session_data"]["second_monitor_width"]
        screen_height = Data_Dictionary["whole_session_data"]["second_monitor_height"]
    except KeyError:
        Logger.print_and_log("No second monitor detected, using local screen.")
        screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
        screen = pygame.display.set_mode((screen_width, screen_height))

    Data_Dictionary["whole_session_data"]["pid"] = ScriptManager.get_participant_id()
    output_log_path = Logger.create_log(filetype=".txt",
                                        log_name=f"{Data_Dictionary['whole_session_data']['pid']}_MSIT_POST")

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
            Logger.print_and_log("Please choose either 'y' or 'n'")

    block_type = ""
    while block_type not in ["I", "C"]:
        block_type = input("Block Type (I/C)?").upper()
        if block_type == "I":
            Logger.print_and_log("Interference Block Selected.")
            block_type = settings.INTERFERENCE_BLOCK
            break
        elif block_type == "C":
            Logger.print_and_log("Control Block Selected.")
            block_type = settings.CONTROL_BLOCK
            break
        else:
            Logger.print_and_log("Please choose either 'I' (Interference) or 'C' (Control)")

    Data_Dictionary["whole_session_data"]["block_type"] = block_type

    Projector.initialize_screen(screen=screen, instructions=settings.MSIT_INSTRUCTIONS)
    Projector.show_instructions(screen=screen, instructions=settings.MSIT_INSTRUCTIONS)

    Projector.show_fixation_cross_rest(screen=screen, dictionary=Data_Dictionary, Get_CSV_if_Error=True)

    for session_num in range(settings.NUM_SESSIONS):
        if session_num % 2 == 0:
            block_type = settings.CONTROL_BLOCK
            seed = settings.CONTROL_SEEDS_POST[session_num // 2]  # Use seed from CONTROL_SEEDS in POST-MSIT tasks
        else:
            block_type = settings.INTERFERENCE_BLOCK
            seed = settings.INTERFERENCE_SEEDS_POST[session_num // 2]  # Use seed from INTERFERENCE_SEEDS in POST-MSIT tasks

        Logger.print_and_log(f"Session {session_num + 1}: Block Type = {'Control' if block_type == settings.CONTROL_BLOCK else 'Interference'}")
        series_list = generate_series(block_type, seed)

        for trial in range(1, settings.TRIALS_PER_SESSION + 1):
            Logger.print_and_log(f"=======Trial {trial}=======")
            Data_Dictionary[f"trial{trial}"] = {}
            Data_Dictionary[f"trial{trial}"]["start_time"] = datetime.now()
            Data_Dictionary[f"trial{trial}"]["block_type"] = block_type
            Data_Dictionary[f"trial{trial}"]["trial_number"] = trial

            # Display the numbers for this trial
            screen.fill((0, 0, 0))  # Clear the screen
            numbers_this_trial = series_list[trial - 1]
            Data_Dictionary[f"trial{trial}"]["number_series"] = numbers_this_trial

            numbers_text = f"{numbers_this_trial[0]}  {numbers_this_trial[1]}  {numbers_this_trial[2]}"
            text_surface = number_font.render(numbers_text, True, (255, 255, 255))

            center_x = int(screen_width // settings.MSIT_SCREEN_DIVISORS_FOR_NUMBERS[0])
            center_y = int(screen_height // settings.MSIT_SCREEN_DIVISORS_FOR_NUMBERS[1])

            text_rect = text_surface.get_rect(center=(center_x, center_y))
            screen.blit(text_surface, text_rect)
            pygame.display.flip()

            Data_Dictionary[f"trial{trial}"] = handle_response(
                trial_dictionary=Data_Dictionary[f"trial{trial}"],
                screen_width=screen_width,
                screen_height=screen_height,
                screen=screen,
                feedback_font=number_font
            )

            # Wait for 1.75 seconds to ensure that the stimulus is shown for the required duration
            pygame.time.wait(int(settings.ISI * 1000))

    Projector.show_fixation_cross_rest(screen=screen, dictionary=Data_Dictionary, Get_CSV_if_Error=True)
    Projector.show_end_message(screen=screen)

run_msit_task()