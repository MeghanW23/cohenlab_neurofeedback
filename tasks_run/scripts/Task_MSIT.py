import pygame
import settings
import Logger
import ScriptManager
import random
import Projector
import time
from datetime import datetime

def get_settings_and_log(data_dictionary: dict) -> dict:
    data_dictionary["whole_session_data"]["pid"] = ScriptManager.get_participant_id()
    Logger.create_log(filetype=".txt", log_name=f"{data_dictionary['whole_session_data']['pid']}_MSIT_PRE")  # create text output log

    while True:
        practice_block_str: str = input("Is this a practice block? (y/n): ")
        if practice_block_str == "y":
            Logger.print_and_log("Ok, running practice block ...")
            data_dictionary["whole_session_data"]["practice_block"] = True
            break

        elif practice_block_str == "n":
            Logger.print_and_log("Ok, running practice block ...")
            data_dictionary["whole_session_data"]["practice_block"] = False
            break

        else:
            Logger.print_and_log("Please type either 'y' or 'n'. Try again.")

    while True:
        msit_type: str = input("Run pre or post MSIT? (pre/post): ")
        if msit_type == "pre":
            Logger.print_and_log("Ok, running pre-msit task ...")
            data_dictionary["whole_session_data"]["msit_type"] = msit_type
            break

        elif msit_type == "post":
            Logger.print_and_log("Ok, running post-msit task ...")
            data_dictionary["whole_session_data"]["msit_type"] = msit_type
            break

        else:
            Logger.print_and_log("Please type either 'pre' or 'post'. Try again.")

    while True:
        starting_block_type: str = input("Run interference or control block first? (i/c): ")
        if starting_block_type == "i":
            Logger.print_and_log("Ok, starting with interference block ...")
            data_dictionary["whole_session_data"]["starting_block_type"] = starting_block_type
            break

        elif starting_block_type == "c":
            Logger.print_and_log("Ok, starting with control block ...")
            data_dictionary["whole_session_data"]["starting_block_type"] = starting_block_type
            break

        else:
            Logger.print_and_log("Please type either 'i' or 'c'. Try again.")

    return data_dictionary
def handle_response(trial_dictionary: dict, screen_width: float, screen_height: float, screen: pygame.Surface, feedback_font, practice: bool) -> dict:
    Response = None
    start_time = pygame.time.get_ticks()
    response_logged = False
    while Response is None or Response == 'NaN':
        trial_dictionary["response"] = None
        current_time = pygame.time.get_ticks()
        if current_time - start_time > settings.MSIT_ISI * 1000:
            if trial_dictionary["response"] is None:
                Logger.print_and_log("No Response For This Trial")
                trial_dictionary["reaction_time"] = None
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if not response_logged and event.type == pygame.KEYDOWN:
                reaction_time = (current_time - start_time) / 1000  # reaction time in seconds
                trial_dictionary["reaction_time"] = reaction_time
                trial_dictionary["time_of_response"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

                if event.key == pygame.K_a or event.key == pygame.K_1:
                    Logger.print_and_log("Response: A/1")
                    Response = 1
                elif event.key == pygame.K_b or event.key == pygame.K_2:
                    Logger.print_and_log("Response: B/2")
                    Response = 2
                elif event.key == pygame.K_c or event.key == pygame.K_3:
                    Logger.print_and_log("Response: C/3")
                    Response = 3
                else:
                    Logger.print_and_log(" ==== INVALID KEYPRESS ==== ")
                    Response = 'NaN'
                trial_dictionary["response"] = Response
                response_logged = True
                trial_dictionary = check_response(trial_dictionary=trial_dictionary,
                                                  screen=screen,
                                                  feedback_font=feedback_font,
                                                  screen_width=screen_width,
                                                  screen_height=screen_height,
                                                  practice=practice,
                                                  current_time=current_time,
                                                  start_time=start_time)

    return trial_dictionary
def generate_series(block_type: int, seed: int) -> list:
    series_list: list = []
    random.seed(seed)

    response_counts = {1:0, 2:0, 3:0}

    for i in range(settings.MSIT_TRIALS_PER_BLOCK):
        series = [0, 0, 0]
        positions = [0,1,2]

        if block_type == settings.MSIT_CONTROL_BLOCK:
            possible_targets = [n for n in [1, 2, 3] if response_counts[n] < 9]
            target_number = random.choice(possible_targets)
            response_counts[target_number] += 1

            random.shuffle(positions)
            series[positions[0]] = target_number

        elif block_type == settings.MSIT_INTERFERENCE_BLOCK:
            same_number = random.choice([n for n in [1, 2, 3] if response_counts[n] < 9])
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
                if block_type == settings.MSIT_CONTROL_BLOCK:
                    possible_targets = [n for n in [1, 2, 3] if response_counts[n] < 9]
                    target_number = random.choice(possible_targets)
                    random.shuffle(positions)
                    series = [0, 0, 0]
                    series[positions[0]] = target_number
                elif block_type == settings.MSIT_INTERFERENCE_BLOCK:
                    same_number = random.choice([n for n in [1, 2, 3] if response_counts[n] < 9])
                    different_number = same_number
                    while different_number == same_number:
                        different_number = random.randint(1, 3)
                    random.shuffle(positions)
                    series = [same_number, same_number, same_number]
                    series[positions[0]] = different_number

        series_list.append(series)

    return series_list
def check_response(trial_dictionary: dict, practice: bool, screen, feedback_font, screen_width: float, screen_height: float, current_time: int, start_time: int) -> dict:
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

    if trial_dictionary["different_number"] == trial_dictionary["response"]:
        trial_dictionary["correct"] = True
        Logger.print_and_log("Response: Correct")
        if practice:
            display_feedback(feedback_str="Correct",
                             feedback_color=(0, 255, 0),
                             feedback_font=feedback_font,
                             screen_width=screen_width,
                             screen_height=screen_height,
                             screen=screen)
    else:
        trial_dictionary["correct"] = False
        if trial_dictionary["response"] == "NaN":
            if practice:
                display_feedback(feedback_str="Invalid Keypress",
                                 feedback_color=(255, 0, 0),
                                 feedback_font=feedback_font,
                                 screen_width=screen_width,
                                 screen_height=screen_height,
                                 screen=screen)
        else:
            Logger.print_and_log(" == INCORRECT RESPONSE == ")
            if practice:
                display_feedback(feedback_str="Incorrect",
                                 feedback_color=(255, 0, 0),
                                 feedback_font=feedback_font,
                                 screen_width=screen_width,
                                 screen_height=screen_height,
                                 screen=screen)

    remaining_time = settings.MSIT_ISI * 1000 - (current_time - start_time)
    if remaining_time > 0:
        time.sleep(remaining_time / 1000)  # Sleep for the remaining time (convert ms to s)

    screen.fill((0, 0, 0))
    pygame.event.clear()
    pygame.display.flip()
    
    return trial_dictionary
def display_feedback(feedback_str: str, feedback_color: tuple, feedback_font, screen_width: float, screen_height: float, screen: pygame.Surface) -> None:
    feedback_surface = feedback_font.render(feedback_str, True, feedback_color)
    feedback_rect = feedback_surface.get_rect(center=(screen_width // 2, (screen_height // 2) - 100))

    # Blit the feedback text
    screen.blit(feedback_surface, feedback_rect)
    pygame.display.flip()
    time.sleep(0.5)  # display for enough time that they see the response

    return None
def run_msit_task():
    pygame.init()  # initialize task

    Data_Dictionary = {'whole_session_data': {}}  # create whole session dictionary

    Data_Dictionary = get_settings_and_log(data_dictionary=Data_Dictionary)

    number_font = pygame.font.Font(None, settings.MSIT_FONT_SIZE_NUMBERS)  # get font size
    random.seed(settings.RANDOM_SEED_VALUE)  # get seed value

    # get screen information
    try:
        Data_Dictionary, screen = Projector.get_monitor_info(dictionary=Data_Dictionary)
        screen_width = Data_Dictionary["whole_session_data"]["second_monitor_width"]
        screen_height = Data_Dictionary["whole_session_data"]["second_monitor_height"]
    except KeyError:
        Logger.print_and_log("No second monitor detected, using local screen.")
        screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
        screen = pygame.display.set_mode((screen_width, screen_height))

    # show instructions
    Projector.initialize_screen(screen=screen, instructions=settings.MSIT_INSTRUCTIONS)
    Projector.show_instructions(screen=screen, instructions=settings.MSIT_INSTRUCTIONS)

    # show 30s rest
    Projector.show_fixation_cross_rest(screen=screen, dictionary=Data_Dictionary, Get_CSV_if_Error=True)
    try:
        control_blocks = 0
        interference_blocks = 0
        for block_num in range(1, settings.MSIT_NUM_BLOCKS + 1):
            Logger.print_and_log(f" ==== Running {block_num} of {settings.MSIT_NUM_BLOCKS} ==== ")

            # setup seed values for block
            if block_num == 1:
                if Data_Dictionary["whole_session_data"]["starting_block_type"] == "c":
                    block_type = settings.MSIT_CONTROL_BLOCK
                    control_blocks += 1
                    seed = settings.CONTROL_SEEDS_PRE[control_blocks]
                else:
                    block_type = settings.MSIT_INTERFERENCE_BLOCK
                    interference_blocks += 1
                    seed = settings.INTERFERENCE_SEEDS_PRE[interference_blocks]

                series_list = generate_series(block_type, seed)
                Data_Dictionary["whole_session_data"]["current_block_type"] = block_type
            else:
                if Data_Dictionary["whole_session_data"]["current_block_type"] == settings.MSIT_CONTROL_BLOCK:
                    block_type = settings.MSIT_INTERFERENCE_BLOCK
                    interference_blocks += 1
                    if Data_Dictionary["whole_session_data"]["msit_type"] == "pre":
                        seed = settings.INTERFERENCE_SEEDS_PRE[control_blocks]
                    else:
                        seed = settings.INTERFERENCE_SEEDS_POST[interference_blocks]
                else:
                    block_type = settings.MSIT_CONTROL_BLOCK
                    control_blocks += 1
                    if Data_Dictionary["whole_session_data"]["msit_type"] == "pre":
                        seed = settings.CONTROL_SEEDS_PRE[block_num // 2]
                    else:
                        seed = settings.CONTROL_SEEDS_POST[block_num // 2]

                series_list = generate_series(block_type, seed)
                Data_Dictionary["whole_session_data"]["current_block_type"] = block_type

            for trial in range(1, settings.MSIT_TRIALS_PER_BLOCK + 1):
                Logger.print_and_log(f"=======Trial {trial}, Block {block_num} =======")
                Data_Dictionary[f"trial{trial}"] = {}
                Data_Dictionary[f"trial{trial}"]["start_time"] = datetime.now()
                Data_Dictionary[f"trial{trial}"]["block_type"] = block_type
                Data_Dictionary[f"trial{trial}"]["trial_number"] = trial

                screen.fill((0, 0, 0))  # Clear the screen
                numbers_this_trial = series_list[trial - 1]
                Data_Dictionary[f"trial{trial}"]["number_series"] = numbers_this_trial
                Logger.print_and_log(f"Number Series: {numbers_this_trial}")

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
                    feedback_font=number_font,
                    practice=Data_Dictionary["whole_session_data"]["practice_block"]
                )

        # close out block
        Projector.show_fixation_cross_rest(screen=screen, dictionary=Data_Dictionary, Get_CSV_if_Error=True)
        Logger.print_and_log("Creating output csv file ...")
        csv_log_path: str = Logger.create_log(filetype=".csv",
                                              log_name=f"output_{Data_Dictionary['whole_session_data']['pid']}_MSIT_PRE")
        Logger.update_log(log_name=csv_log_path, dictionary_to_write=Data_Dictionary)
        Projector.show_end_message(screen=screen)


    except KeyboardInterrupt:
        print(" ---- Keyboard Interrupt Detected ----- ")
        Logger.print_and_log("Creating output csv file ...")
        csv_log_path: str = Logger.create_log(filetype=".csv",
                                              log_name=f"output_{Data_Dictionary['whole_session_data']['pid']}_MSIT_PRE")
        Logger.update_log(log_name=csv_log_path, dictionary_to_write=Data_Dictionary)


run_msit_task()