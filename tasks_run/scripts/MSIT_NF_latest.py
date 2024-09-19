import random
import pygame
from datetime import datetime
import settings
import Logger

CONTROL_BLOCK = 333
INTERFERENCE_BLOCK = 444
TRIALS_PER_SESSION = 24
NUM_SESSIONS = 8
ISI = 1.75  # seconds
CONTROL_SEEDS = [42, 88, 3, 78]  # Separate seeds for control blocks
INTERFERENCE_SEEDS = [55, 99, 50, 18]  # Separate seeds for interference blocks


def generate_series(block_type: int, seed: int) -> list:
    series_list: list = []
    random.seed(seed)  # Set the seed for generating the series

    for i in range(TRIALS_PER_SESSION):
        series = [0, 0, 0]
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
            series = [same_number, same_number, same_number]
            series[positions[0]] = different_number

        series_list.append(series)

    return series_list

def run_msit_task():
    Data_Dictionary = {}

    pygame.init()
    number_font = pygame.font.Font(None, 74)  # Placeholder for font size
    screen = pygame.display.set_mode((800, 600))  # Placeholder for screen dimensions

    for session_num in range(NUM_SESSIONS):
        # Alternate between control and interference blocks
        if session_num % 2 == 0:
            block_type = CONTROL_BLOCK
            seed = CONTROL_SEEDS[session_num // 2]  # Use seed for control blocks
        else:
            block_type = INTERFERENCE_BLOCK
            seed = INTERFERENCE_SEEDS[session_num // 2]  # Use seed for interference blocks

        # Log session details
        print(
            f"Session {session_num + 1}: Block Type = {'Control' if block_type == CONTROL_BLOCK else 'Interference'}, Seed = {seed}")

        # Generate the series for the current session using the assigned seed
        series_list = generate_series(block_type, seed)

        for trial in range(1, TRIALS_PER_SESSION + 1):
            print(f"======= Trial {trial} =======")
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

            center_x = screen.get_width() // 2
            center_y = screen.get_height() // 2

            text_rect = text_surface.get_rect(center=(center_x, center_y))
            screen.blit(text_surface, text_rect)
            pygame.display.flip()

            # Wait for response (or no response)
            Data_Dictionary[f"trial{trial}"] = handle_response(
                trial_dictionary=Data_Dictionary[f"trial{trial}"],
                screen_width=screen.get_width(),
                screen_height=screen.get_height(),
                screen=screen,
                feedback_font=number_font
            )

            # Wait for 1.75 seconds to ensure stimulus duration
            pygame.time.wait(int(ISI * 1000))


def handle_response(trial_dictionary: dict, screen_width: float, screen_height: float, screen, feedback_font) -> dict:
    Response = None
    start_time = pygame.time.get_ticks()
    feedback_font = pygame.font.Font(None, settings.MSIT_FONT_SIZE_FEEDBACK)

    while Response is None:
        current_time = pygame.time.get_ticks()

        # Check if 1.75 seconds have passed
        if current_time - start_time > ISI * 1000:
            if trial_dictionary.get("response") is None:
                Logger.print_and_log("No Response For This Trial")
                trial_dictionary["reaction_time"] = None

                Logger.print_and_log(
                    f"Trial {trial_dictionary['trial_number']} - Block: {'Control' if trial_dictionary['block_type'] == CONTROL_BLOCK else 'Interference'}")
                Logger.print_and_log(f"Number Series: {trial_dictionary['number_series']}")
                Logger.print_and_log("No Response Recorded")

            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                trial_dictionary["reaction_time"] = (current_time - start_time) / 1000  # Convert to seconds
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

                # Record feedback
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

    # Log the different number
    Logger.print_and_log(f"Trial {trial_dictionary['trial_number']} - Block: {'Control' if trial_dictionary['block_type'] == CONTROL_BLOCK else 'Interference'}")
    Logger.print_and_log(f"Number Series: {trial_dictionary['number_series']}")
    Logger.print_and_log(f"Different Number: {trial_dictionary['different_number']}")

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


run_msit_task()