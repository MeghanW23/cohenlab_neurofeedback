from typing import List
import pygame
import settings
import Logger
import ScriptManager
import random
import Projector
import FileHandler
import time
from datetime import datetime

def get_settings_and_log(data_dictionary: dict) -> dict:
    data_dictionary["whole_session_data"]["pid"] = FileHandler.validate_inputted_pid_is_new(inputted_pid=ScriptManager.get_participant_id())
    Logger.create_log(filetype=".txt", log_name=f"{data_dictionary['whole_session_data']['pid']}_MSIT_PRE")  # create text output log

    while True:
        practice_block_str: str = input("Is this a practice block? (y/n): ")
        if practice_block_str == "y":
            Logger.print_and_log("Ok, running practice block ...")
            data_dictionary["whole_session_data"]["practice_block"] = True
            break

        elif practice_block_str == "n":
            Logger.print_and_log("Ok, not running practice block ...")
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

    Logger.print_and_log("Starting with a control block.")
    data_dictionary["whole_session_data"]["starting_block_type"] = "c"

    return data_dictionary
def handle_response(trial_dictionary: dict, 
                    screen_width: float, 
                    screen_height: float, 
                    screen: pygame.Surface, 
                    feedback_font, 
                    practice: bool, 
                    score_csv_path: str) -> dict:
    Response = None
    start_time = pygame.time.get_ticks()
    response_logged = False
    while Response is None or Response == 'NaN':
        trial_dictionary["response"] = None
        current_time = pygame.time.get_ticks()
        if current_time - start_time > settings.MSIT_ISI * 1000:
            if trial_dictionary["response"] is None:
                Logger.print_and_log(" ======================== ")
                Logger.print_and_log("No Response For This Trial")
                Logger.print_and_log(" ======================== ")
                trial_dictionary["reaction_time"] = None
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if not response_logged and event.type == pygame.KEYDOWN:
                if not event.key == pygame.K_s: # scanner impulse mapped to 's' keypress
                    reaction_time = (current_time - start_time) / 1000  # reaction time in seconds
                    trial_dictionary["reaction_time"] = reaction_time
                    trial_dictionary["time_of_response"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

                    if event.key == pygame.K_b or event.key == pygame.K_1:
                        Logger.print_and_log("Response: B/1")
                        Response = 1
                    elif event.key == pygame.K_a or event.key == pygame.K_2:
                        Logger.print_and_log("Response: A/2")
                        Response = 2
                    elif event.key == pygame.K_c or event.key == pygame.K_3:
                        Logger.print_and_log("Response: C/3")
                        Response = 3
                    elif event.key == pygame.K_ESCAPE:
                        Response = 'Quitting'
                        pass
                    else:
                        Logger.print_and_log(" ==== INVALID KEYPRESS ==== ")
                        trial_dictionary["invalid_keypress"] = True
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
                                                    start_time=start_time, 
                                                    score_csv_path=score_csv_path)
    if Response is None:
        Logger.update_score_csv(action="add_to_csv", 
                                task="msit", 
                                path_to_csv=score_csv_path, 
                                score="no_press", 
                                tr=trial_dictionary["total_trial_count"],
                                additional_data=[trial_dictionary["block_type"], trial_dictionary["block_num"], trial_dictionary["trial_number"]])
    
    return trial_dictionary
def generate_series(block_type: int, seed: int) -> List[List[int]]:
    # return a list of 3-int-lists, where each 3-int-list is 1 trial's digits to show
    # see: https://github.com/ccraddock/msit?tab=readme-ov-file 


    # make a 1-trial series of 3 numbers, where the paired digits are zero and the position of the target digit corresponds to its location.
    def make_control_trial_series() -> List[int]:

        # the non-target value must be zero 
        control_series: List[int] = [0, 0, 0] 

        # get a random choice of what target to use
        target_digit: int = random.choice([1, 2, 3])

        # put the target digit at its position in the list: 
        control_series[target_digit - 1] = target_digit 

        return control_series


    # make a 1-trial series of 3 numbers, where tthe distractor digits are non-zero (other digits) and the target digits location is not the same as its value.
    def make_interference_trial_series() -> List[int]: 

        # get random distractor digit and fill the interference series with that digit 
        distractor_digit: int = random.choice([1, 2, 3])
        interference_series: List[int] = [distractor_digit, distractor_digit, distractor_digit] 

        # get a random target digit that isn't the distractor_digit
        target_digit: int = random.choice([num for num in range(1, 4) if not num == distractor_digit]) 
        
        # get the location of the target digit in the interference_series (the target digits location cannot be the same as its value)
        target_location: int = random.choice([num for num in range(0, 3) if not num == target_digit - 1])
        
        # put the target digit at its target location in the list
        interference_series[target_location] = target_digit 

        return interference_series

    
    random.seed(seed) # set the random seed 

    whole_block_series_list: List[List[int]] = [] # initialize the list of all trials to return

    for _ in range(1, settings.MSIT_TRIALS_PER_BLOCK + 1): 
        
       
        if block_type == settings.MSIT_CONTROL_BLOCK:
            
            while True: # keep getting a possible 3-int series for this trial until it is not a duplicate of the last trial

                # single-trial control series 
                control_series: List[int] = make_control_trial_series()

                if len(whole_block_series_list) == 0:
                    whole_block_series_list.append(control_series) # add to whole-block list

                    break # start next trial

                elif control_series != whole_block_series_list[-1]:

                    whole_block_series_list.append(control_series) # add to whole-block list

                    break # start next trial

        if block_type == settings.MSIT_INTERFERENCE_BLOCK:

            while True: # keep getting a possible 3-int series for this trial until it is not a duplicate of the last trial
                
                # single-trial interference series 
                interference_series: List[int] = make_interference_trial_series()

                if len(whole_block_series_list) == 0:
                    whole_block_series_list.append(interference_series) # add to whole-block list

                    break # start next trial

                elif interference_series != whole_block_series_list[-1]:

                    whole_block_series_list.append(interference_series) # add to whole-block list

                    break # start next trial

    return whole_block_series_list
def check_response(trial_dictionary: dict, practice: bool, screen, feedback_font, screen_width: float, screen_height: float, current_time: int, start_time: int, score_csv_path) -> dict:
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
        Logger.update_score_csv(action="add_to_csv", 
                                task="msit", 
                                path_to_csv=score_csv_path, 
                                score="correct", 
                                tr=trial_dictionary["total_trial_count"],
                                additional_data=[trial_dictionary["block_type"], trial_dictionary["block_num"], trial_dictionary["trial_number"]])
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
            Logger.update_score_csv(action="add_to_csv", 
                                    task="msit", 
                                    path_to_csv=score_csv_path, 
                                    score="invalid_press", 
                                    tr=trial_dictionary["total_trial_count"],
                                    additional_data=[trial_dictionary["block_type"], trial_dictionary["block_num"], trial_dictionary["trial_number"]])
            if practice:
                display_feedback(feedback_str="Invalid Keypress",
                                 feedback_color=(255, 0, 0),
                                 feedback_font=feedback_font,
                                 screen_width=screen_width,
                                 screen_height=screen_height,
                                 screen=screen)
        elif trial_dictionary["response"] == "Quitting":
            pass
        else:
            Logger.print_and_log(" ======================== ")
            Logger.print_and_log(" == INCORRECT RESPONSE == ")
            Logger.print_and_log(" ======================== ")
            Logger.update_score_csv(action="add_to_csv", 
                                    task="msit", 
                                    path_to_csv=score_csv_path, 
                                    score="incorrect", 
                                    tr=trial_dictionary["total_trial_count"],
                                    additional_data=[trial_dictionary["block_type"], trial_dictionary["block_num"], trial_dictionary["trial_number"]])
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
    resized_surface = pygame.transform.scale(feedback_surface, (300, 100))
    feedback_rect = resized_surface.get_rect(center=(screen_width // settings.MSIT_SCREEN_DIVISORS_FOR_FEEDBACK[0], (screen_height // settings.MSIT_SCREEN_DIVISORS_FOR_FEEDBACK[1]) - settings.FEEDBACK_COORD_OFFSET))

    # Blit the feedback text
    screen.blit(resized_surface, feedback_rect)
    pygame.display.flip()
    time.sleep(0.5)  # display for enough time that they see the response

    return None
def check_block_statistics(data_dictionary: dict, block_num: int) -> dict:
    trials_correct = 0
    trials_skipped = 0
    invalid_keypresses = 0
    for key, trial_dictionary in data_dictionary.items():
        if "trial" in key:
            if "correct" in trial_dictionary and trial_dictionary["correct"]:
                trials_correct += 1
            if trial_dictionary["reaction_time"] is None:
                trials_skipped += 1
            if "invalid_keypress" in trial_dictionary:
                invalid_keypresses += 1
        else:
            continue

    data_dictionary["whole_session_data"][f"block{block_num}_stats"] = {}
    data_dictionary["whole_session_data"][f"block{block_num}_stats"]["trials_correct"] = trials_correct
    data_dictionary["whole_session_data"][f"block{block_num}_stats"]["trials_skipped"] = trials_skipped
    data_dictionary["whole_session_data"][f"block{block_num}_stats"]["percent_correct"] = round(trials_correct / settings.MSIT_TRIALS_PER_BLOCK, 2)
    data_dictionary["whole_session_data"][f"block{block_num}_stats"]["invalid_keypresses"] = invalid_keypresses


    Logger.print_and_log("============================= ENDING BLOCK STATISTICS ===================================")
    Logger.print_and_log(f"Percent of Trials Correct: {(round(trials_correct / settings.MSIT_TRIALS_PER_BLOCK, 2)) * 100}%")
    Logger.print_and_log(f"Percent of Trials with Invalid Responses: {(round(invalid_keypresses / settings.MSIT_TRIALS_PER_BLOCK, 2)) * 100}%")
    Logger.print_and_log(f"Percent of Trials Skipped: {(round(trials_skipped / settings.MSIT_TRIALS_PER_BLOCK, 2)) * 100}%")

    if (invalid_keypresses / settings.MSIT_TRIALS_PER_BLOCK) > settings.MSIT_PERCENT_INVALID_BEFORE_WARNING:
        Logger.print_and_log("===================== ATTENTION =====================")
        Logger.print_and_log(f"Subject pressed an invalid key on more than {(settings.MSIT_PERCENT_INVALID_BEFORE_WARNING * 100)}% of the trials. \nConsider stopping the task and making sure they know what keys to press.")
        Logger.print_and_log("===================== ATTENTION =====================")

    elif (trials_skipped / settings.MSIT_TRIALS_PER_BLOCK) > settings.MSIT_PERCENT_SKIPPED_BEFORE_WARNING:
        Logger.print_and_log("===================== ATTENTION =====================")
        Logger.print_and_log(f"Subject skipped more than {(settings.MSIT_PERCENT_SKIPPED_BEFORE_WARNING * 100)}% of trials this block.\nConsider stopping the task and making sure they know what what to do.")
        Logger.print_and_log("===================== ATTENTION =====================")

    elif (trials_correct / settings.MSIT_TRIALS_PER_BLOCK) < settings.MSIT_PERCENT_WRONG_BEFORE_WARNING:
        Logger.print_and_log("===================== ATTENTION =====================")
        Logger.print_and_log(f"Subject got less than {(settings.MSIT_PERCENT_WRONG_BEFORE_WARNING * 100)}% accurate this block.\nConsider stopping the task and making sure they know what what to do.")
        Logger.print_and_log("===================== ATTENTION =====================")

    Logger.print_and_log("============================= ENDING BLOCK STATISTICS ===================================")

    return data_dictionary
def run_msit_task():
    try: 
        pygame.init()  # initialize task

        Logger.InterruptHandler.start_keyboard_listener() # start keyboard listener for esc key pressed

        Data_Dictionary = {'whole_session_data': {}}  # create whole session dictionary

        Data_Dictionary = get_settings_and_log(data_dictionary=Data_Dictionary)

        number_font = pygame.font.Font(None, settings.MSIT_FONT_SIZE_NUMBERS)  # get font size
        random.seed(settings.RANDOM_SEED_VALUE)  # get seed value

                
        Data_Dictionary["whole_session_data"]["path_to_csv"] = Logger.update_score_csv(action="create_csv", 
                                                                                    task="msit", 
                                                                                    path_to_csv_dir=settings.MSIT_SCORE_LOG_DIR, 
                                                                                    pid=Data_Dictionary["whole_session_data"]["pid"],
                                                                                    additional_headers=["trial_type", "block_num", "trial_in_block"])

        # get screen information
        Data_Dictionary, screen = Projector.get_monitor_info(dictionary=Data_Dictionary)
        screen_width = Data_Dictionary["whole_session_data"]["second_monitor_width"]
        screen_height = Data_Dictionary["whole_session_data"]["second_monitor_height"]

        # write to vnc viewer log to open the vnc 
        Logger.write_to_open_viewer_log()

        # show instructions
        Projector.initialize_screen(screen=screen, instructions=settings.MSIT_INSTRUCTIONS, dictionary=Data_Dictionary)
        Projector.show_msit_instructions(screen=screen, instructions=settings.MSIT_INSTRUCTIONS)

        Logger.update_score_csv(action="add_to_csv", 
                                task="msit", 
                                path_to_csv=Data_Dictionary["whole_session_data"]["path_to_csv"], 
                                score="rest", 
                                tr=0,
                                additional_data=["rest", 0, 0])
        # show 30s rest
        Projector.show_fixation_cross_rest(screen=screen)
        
        # get total trials for graphing
        total_trials: int = 0
        control_blocks: int = -1
        interference_blocks: int = -1
        for block_num in range(1, settings.MSIT_NUM_BLOCKS + 1):
            Logger.print_and_log(f" ==== Running {block_num} of {settings.MSIT_NUM_BLOCKS} ==== ")

            # setup seed values for block
            if block_num == 1:
                block_type = settings.MSIT_CONTROL_BLOCK
                control_blocks += 1
                seed = settings.CONTROL_SEEDS_PRE[control_blocks] if Data_Dictionary ["whole_session_data"]["msit_type"] == "pre" else settings.CONTROL_SEEDS_POST[control_blocks]
            else:
                if Data_Dictionary["whole_session_data"].get("current_block_type") == settings.MSIT_CONTROL_BLOCK:
                    block_type = settings.MSIT_INTERFERENCE_BLOCK
                    interference_blocks += 1
                    seed = settings.INTERFERENCE_SEEDS_PRE[interference_blocks] if Data_Dictionary["whole_session_data"]["msit_type"] == "pre" else settings.INTERFERENCE_SEEDS_POST[interference_blocks]
                else:
                    block_type = settings.MSIT_CONTROL_BLOCK
                    control_blocks += 1
                    seed = settings.CONTROL_SEEDS_PRE[control_blocks] if Data_Dictionary["whole_session_data"]["msit_type"] == "pre" else settings.CONTROL_SEEDS_POST[control_blocks]

            series_list = generate_series(block_type, seed)
            Data_Dictionary["whole_session_data"]["current_block_type"] = block_type

            for trial in range(1, settings.MSIT_TRIALS_PER_BLOCK + 1):
                
                if Logger.InterruptHandler.if_interrupted(): raise KeyboardInterrupt # check for recent 'esc' key presses

                total_trials += 1
                
                Logger.print_and_log(f"=======Trial {trial}, Block {block_num} =======")
                Data_Dictionary[f"trial{trial}"] = {}
                Data_Dictionary[f"trial{trial}"]["start_time"] = datetime.now()
                Data_Dictionary[f"trial{trial}"]["total_trial_count"] = total_trials
                Data_Dictionary[f"trial{trial}"]["block_type"] = block_type
                Data_Dictionary[f"trial{trial}"]["trial_number"] = trial
                Data_Dictionary[f"trial{trial}"]["block_num"] = block_num;

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
                    practice=Data_Dictionary["whole_session_data"]["practice_block"],
                    score_csv_path=Data_Dictionary["whole_session_data"]["path_to_csv"]
                )

                if trial == settings.MSIT_TRIALS_PER_BLOCK:
                    Data_Dictionary = check_block_statistics(data_dictionary=Data_Dictionary, block_num=block_num)

        # close out block
        if Logger.InterruptHandler.if_interrupted(): raise KeyboardInterrupt
        Projector.show_fixation_cross_rest(screen=screen)
        Logger.print_and_log("Creating output csv file ...")
        csv_log_path: str = Logger.create_log(filetype=".csv",
                                                log_name=f"output_{Data_Dictionary['whole_session_data']['pid']}_MSIT_PRE")
        Logger.update_log(log_name=csv_log_path, dictionary_to_write=Data_Dictionary)
        Projector.show_end_message(screen=screen, dictionary=Data_Dictionary)

    except KeyboardInterrupt:
        print(" ---- Keyboard Interrupt Detected ----- ")
        Logger.print_and_log("Creating output csv file ...")
        csv_log_path: str = Logger.create_log(filetype=".csv",
                                              log_name=f"output_{Data_Dictionary['whole_session_data']['pid']}_MSIT_PRE")
        Logger.update_log(log_name=csv_log_path, dictionary_to_write=Data_Dictionary)

run_msit_task()