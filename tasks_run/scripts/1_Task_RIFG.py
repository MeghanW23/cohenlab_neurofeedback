from datetime import datetime
import os
import random
import csv
import time
import pandas as pd
import FileHandler
import Projector
import settings 
import pygame
import Logger
import ScriptManager
import Calculator
from typing import List, Tuple

""" FUNCTIONS """
def get_task() -> str: 
    while True:
        task_type: str = input("Run pre or post rIFG? (pre/post): ")
        if task_type == "pre":
            Logger.print_and_log("Ok, running pre-rIFG task ...")
            return task_type
        elif task_type == "post":
            Logger.print_and_log("Ok, running post-rIFG task ...")
            return task_type
        else:
            Logger.print_and_log("Please type either 'pre' or 'post'. Try again.")

def get_if_practice() -> bool:
    while True:
        practice: str = input("Practice? (y/n): ")
        if practice == "y":
            Logger.print_and_log("Ok, running practice...")
            return True
        elif practice == "n":
            Logger.print_and_log("Ok, nbot running practice ...")
            return False
        else:
            Logger.print_and_log("Please type either 'y' or 'n'. Try again.")

def update_log_names_if_practice(input_path: str) -> str:

    # get new log name
    new_basename = "practice_" + os.path.basename(input_path)
    
    # rename file 
    if os.path.exists(input_path): 
        os.rename(input_path, os.path.join(os.path.dirname(input_path), new_basename))

    # return path
    return os.path.join(os.path.dirname(input_path), new_basename)
    
def make_event_csv(participant_id: str, task_type: str, timestamp: str, starting_onset: int, starting_duration: int, starting_trial_type:str) -> str: 
    event_csv_path: str = os.path.join(settings.RIFG_EVENT_CSV_DIR, 
                                       f"{participant_id}_rifg_task_{task_type}RIFG_events_{timestamp}.csv")

    add_to_event_csv(event_csv_path=event_csv_path,
                     onset=starting_onset,
                     duration=starting_duration,
                     trial_type=starting_trial_type)
    
    return event_csv_path

def add_to_event_csv(event_csv_path: str,  onset: int, duration: int, trial_type: int,):
    pd.DataFrame([{
        "onset": onset,
        "duration": duration,
        "trial_type": trial_type
    }]).to_csv(path_or_buf=event_csv_path,
               mode='a',
               header=False,
               index=False)

def print_data_dictionary(data_dictionary:dict, name: str = "outermost dict"):
    Logger.print_and_log(f"--- Dictionary {name} -----")
    for key, value in data_dictionary.items():
        if isinstance(value, dict):
            print_data_dictionary(data_dictionary=value, name=key)
        else:
            Logger.print_and_log(f"KEY: {key}, VALUE: {value}")
    Logger.print_and_log(f"--- Dictionary {name} -----")

def convert_isi_csv_to_list(isi_csv_path: str) -> List[float]: 
    isi_list: List[float] = []
    with open(file=isi_csv_path) as f:
        reader = csv.reader(f)
        for index, value in enumerate(reader, start=1):
            value = value[0]
            # add all str vals that can be converted to floats (so not headers)
            try:
                float(value)
                isi_list.append(value)
            except ValueError:
                pass
    if len(isi_list) != settings.RIFG_N_TRIALS:
        raise ValueError(f"Mismatch between number of ISI values ({len(isi_list)}) and expected number of trials ({settings.RIFG_N_TRIALS}).")
    else:
        return isi_list

def validate_paths( warn_or_raise: str, path_and_name_list: List[Tuple[str, str]]):
    
    if not warn_or_raise in ("warn", "raise"):
        raise ValueError(f"Options for 1_Task_RIFG.validate_paths() argument: warn_or_raise are 'warn' or 'raise'.\n You inputted: {warn_or_raise}") 
    
    for name, path in path_and_name_list: 
        if not os.path.exists(path=path):
            if warn_or_raise == "warn":
                Logger.print_and_log(f"- WARNING-\n{name}: {path} does not exist\n- WARNING-")
            else:
                raise FileNotFoundError(f"{name}: {path} does not exist")
            
def choose_stimulus() -> str:

    return random.choice(["buzz", "buzz", "buzz", "bear"]) # 75% chance of Buzz

def run_trial(stimulus: str, data_dictionary: dict):
    # clear pressed a counter 
    button_presses: List[Tuple[str, datetime]] = []

    # clear result 
    result = None

    # get starting time for showing icon
    start_time = datetime.now()

    # clear any accidental button presses during fixation
    pygame.event.clear() 
        
    # show icon
    blit_icon(stimulus=stimulus, 
              data_dictionary=data_dictionary)

    # wait for a response
    while True:
       
        elapsed_time = (datetime.now() - start_time).total_seconds()
        
        if elapsed_time < settings.RIFG_TRIAL_DURATION:
            for event in pygame.event.get():
                
                # If they pressed A 
                if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
                    # blit pressed button feedback at first button press if practice 
                    if button_presses == [] and data_dictionary['whole_session_data']['practice']:
                        blit_button_press(data_dictionary=data_dictionary)


                    Logger.print_and_log("Pressed A")
                    button_presses.append(('a', datetime.now()))
                    pygame.event.clear() 

                # If they pressed B 
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                    # blit pressed button feedback at first button press if practice 
                    if button_presses == [] and data_dictionary['whole_session_data']['practice']:
                        blit_button_press(data_dictionary=data_dictionary)


                    Logger.print_and_log("Pressed B")
                    button_presses.append(('b', datetime.now()))
                    pygame.event.clear() 

            
            # first button press dictates result
            if result == None:
                result = "hit" if stimulus == "buzz" else "false_alarm"
                
            
        else:
            # participant has ran out of time 
            if button_presses == []:
                result = "miss" if stimulus == "buzz" else "correct_rejection"
            
            data_dictionary[f'trial{trial}']['result'] = result
            data_dictionary[f'trial{trial}']['button_presses'] = button_presses

            Logger.print_and_log(f"Result: {data_dictionary[f'trial{trial}']['result']}")

            return data_dictionary

def blit_icon(stimulus: str, data_dictionary:dict):
    if stimulus == "buzz":
        screen.blit(buzz_resized, (data_dictionary["whole_session_data"]["second_monitor_width"] // 
                                   settings.BUZZ_BEAR_LOCATION_SECMON_WIDTH_DIVISOR - data_dictionary["whole_session_data"]["buzz_width"] // 
                                   settings.BUZZ_BEAR_LOCATION_WIDTH_DIVISOR, data_dictionary["whole_session_data"]["second_monitor_height"] // 
                                   settings.BUZZ_BEAR_LOCATION_SECMON_HEIGHT_DIVISOR - data_dictionary["whole_session_data"]["buzz_height"] // 
                                   settings.BUZZ_BEAR_LOCATION_HEIGHT_DIVISOR))
        pygame.display.flip()
    else:
        screen.blit(bear_resized, (data_dictionary["whole_session_data"]["second_monitor_width"] // 
                                   settings.BUZZ_BEAR_LOCATION_SECMON_WIDTH_DIVISOR - data_dictionary["whole_session_data"]["bear_width"] // 
                                   settings.BUZZ_BEAR_LOCATION_WIDTH_DIVISOR, data_dictionary["whole_session_data"]["second_monitor_height"] // 
                                   settings.BUZZ_BEAR_LOCATION_SECMON_HEIGHT_DIVISOR - data_dictionary["whole_session_data"]["bear_height"] // 
                                   settings.BUZZ_BEAR_LOCATION_HEIGHT_DIVISOR))
        pygame.display.flip()

def blit_button_press(data_dictionary:dict):
    screen.blit(keypress_resized,(data_dictionary["whole_session_data"]["second_monitor_width"] // 
                                   settings.KEYPRESS_LOCATION_SECMON_WIDTH_DIVISOR - data_dictionary["whole_session_data"]["keypress_width"] // 
                                   settings.KEYPRESS_LOCATION_WIDTH_DIVISOR, data_dictionary["whole_session_data"]["second_monitor_height"] // 
                                   settings.KEYPRESS_LOCATION_SECMON_HEIGHT_DIVISOR - data_dictionary["whole_session_data"]["keypress_height"] // 
                                   settings.KEYPRESS_LOCATION_HEIGHT_DIVISOR))
    pygame.display.flip()

""" SETUP PATHS AND KNOBS """
# setup data dictionary 
data_dictionary: dict = {
    'whole_session_data': {"pid": ScriptManager.get_participant_id(),
                           "script_starting_time": Calculator.get_time(action="get_time"),
                           "task_type": get_task(),
                           "practice": get_if_practice()},
    'session_vars': {"onset": 0.0,
                     "duration": settings.REST_DURATION,
                     "trial_type": 'rest'}
    }

# update data dictionary using the already-added data dictionary elements
data_dictionary['whole_session_data'].update({
    "textlog_path": Logger.create_log(filetype=".txt", log_name=f"{data_dictionary['whole_session_data']['pid']}_{data_dictionary['whole_session_data']['task_type']}_rifg_log"),
    "roi_mask_path": FileHandler.get_most_recent(action="roi_mask"),
    "dicom_dir_path": FileHandler.get_most_recent(action="dicom_dir"),
    "seed": settings.RIFG_POST_SEED if data_dictionary['whole_session_data']['task_type'] == "post" else settings.RIFG_PRE_SEED,
    "isi_list_path": settings.RIFG_postRIFG_ISI if data_dictionary['whole_session_data']['task_type'] == "post" else settings.RIFG_preRIFG_ISI,
    "score_csv_path": Logger.update_score_csv(action="create_csv", 
                                              task="rifg", 
                                              path_to_csv_dir=settings.RIFG_SCORE_LOG_DIR, 
                                              pid=data_dictionary["whole_session_data"]["pid"], 
                                              additional_headers=["stimulus_type"]),
    "csvlog_path": Logger.create_log(timestamp=data_dictionary["whole_session_data"]["script_starting_time"].strftime("%Y%m%d_%Hh%Mm%Ss"),
                                     filetype=".csv", 
                                     log_name=f"{data_dictionary['whole_session_data']['pid']}_rifg_task_{data_dictionary['whole_session_data']['task_type']}"),
    "event_csv_path": make_event_csv(participant_id=data_dictionary['whole_session_data']['pid'],
                                     task_type=data_dictionary['whole_session_data']['task_type'],
                                     timestamp=data_dictionary["whole_session_data"]["script_starting_time"].strftime("%Y%m%d_%Hh%Mm%Ss"),
                                     starting_onset=data_dictionary['session_vars']['onset'],
                                     starting_duration=data_dictionary['session_vars']['duration'],
                                     starting_trial_type=data_dictionary['session_vars']['trial_type'])})

# update log names to indicate it's practice, if its practice
data_dictionary['whole_session_data']['textlog_path'] = update_log_names_if_practice(input_path=data_dictionary['whole_session_data']['textlog_path'])
data_dictionary['whole_session_data']['score_csv_path'] = update_log_names_if_practice(input_path=data_dictionary['whole_session_data']['score_csv_path'])
data_dictionary['whole_session_data']['csvlog_path'] = update_log_names_if_practice(input_path=data_dictionary['whole_session_data']['csvlog_path'])
data_dictionary['whole_session_data']['event_csv_path'] = update_log_names_if_practice(input_path=data_dictionary['whole_session_data']['event_csv_path'])

# update data dictionary using the already-added data dictionary elements (again)
data_dictionary['whole_session_data'].update({
    "isi_list": convert_isi_csv_to_list(isi_csv_path=data_dictionary['whole_session_data']['isi_list_path'])
})

# set random seed 
random.seed(data_dictionary['whole_session_data']['seed'])

# make sure all paths exist:
validate_paths(warn_or_raise="raise",
               path_and_name_list= [
                   ('roi_mask_path', data_dictionary['whole_session_data']['roi_mask_path']),
                   ('dicom_dir_path', data_dictionary['whole_session_data']['dicom_dir_path']),
                   ('isi_list_path', data_dictionary['whole_session_data']['isi_list_path']),
                   ('score_csv_path', data_dictionary['whole_session_data']['score_csv_path']),
                   ('csvlog_path', data_dictionary['whole_session_data']['csvlog_path']),
                   ('event_csv_path', data_dictionary['whole_session_data']['event_csv_path']),
               ])

""" SETUP DISPLAY AND ICONS """
# get monitor dimensions and info
data_dictionary, screen = Projector.get_monitor_info(dictionary=data_dictionary)

# load & resize buzz
buzz: pygame.Surface = pygame.image.load(settings.BUZZ_PATH)
new_width_buzz: float = data_dictionary["whole_session_data"]["second_monitor_width"] // settings.BUZZ_WIDTH_DIVISOR 
new_height_buzz: float = data_dictionary["whole_session_data"]["second_monitor_height"] // settings.BUZZ_HEIGHT_DIVISOR
buzz_resized: pygame.Surface = pygame.transform.scale(buzz, (new_width_buzz, new_height_buzz))

# load & resize bear
bear: pygame.Surface = pygame.image.load(settings.BEAR_PATH)
new_width_bear: float = data_dictionary["whole_session_data"]["second_monitor_width"] // settings.BEAR_WIDTH_DIVISOR
new_height_bear: float = data_dictionary["whole_session_data"]["second_monitor_height"] // settings.BEAR_HEIGHT_DIVISOR
bear_resized: pygame.Surface = pygame.transform.scale(bear, (new_width_bear, new_height_bear))

# load & resize 'pressed a' icon
pressed_a: pygame.Surface = pygame.image.load(settings.RIFG_KEYPRESS_ICON_PATH)
keypress_resized: pygame.Surface = pygame.transform.scale(pressed_a, (settings.KEYPRESS_WIDTH, settings.KEYPRESS_HEIGHT))

# add icon dimensions to the data_dictionary 
data_dictionary['whole_session_data'].update({
    "buzz_width": buzz_resized.get_width(),
    "buzz_height": buzz_resized.get_height(),
    "bear_width": bear_resized.get_width(),
    "bear_height": bear_resized.get_height(),
    "keypress_width":  keypress_resized.get_width(),
    "keypress_height":  keypress_resized.get_height()
})

""" START DISPLAYING TASK """
# start keyboard listener to listen for esc key pressed - will trigger KeyboardInterupt if pressed
Logger.InterruptHandler.start_keyboard_listener() 
try:

    """ DISPLAY INSTRUCTIONS """
    Projector.initialize_screen(screen=screen, instructions=["Welcome To The Experiment!", "Please Wait ..."], dictionary=data_dictionary)
    Projector.show_instructions(screen=screen, instructions=settings.RIFG_INSTRUCTIONS)

    """ DISPLAY STARTING REST """
    Projector.show_fixation_cross_rest(screen=screen) 
    pygame.display.flip()

    """ DISPLAY TASK """
    for trial in range(1, settings.RIFG_N_TRIALS + 1):

        """ SETUP TRIAL """
        Logger.print_and_log(f" ==== Starting Trial {trial} ==== ")

        if Logger.InterruptHandler.if_interrupted(): raise KeyboardInterrupt # check for recent 'esc' key presses

        # update data dictionary, add subdict for the trial
        data_dictionary.update({
            f"trial{trial}": {
                "starting_trial_time": datetime.now(),
                "stimulus": choose_stimulus(),
                "isi": float(data_dictionary['whole_session_data']['isi_list'][trial - 1])},
            "session_vars": {
                # onset = onset (of last trial) + duration (of last trial) + ISI (before this trial is blit)
                "onset": float(data_dictionary['session_vars']['onset']) + float(data_dictionary['whole_session_data']['isi_list'][trial - 1]) + float(data_dictionary['session_vars']['duration']),
                "duration": settings.RIFG_TRIAL_DURATION,
                "trial_type": "task"}
        })

        Logger.print_and_log(f"Stimulus: {data_dictionary[f'trial{trial}']['stimulus']}")
        # update event csv
        add_to_event_csv(event_csv_path=data_dictionary['whole_session_data']['event_csv_path'],
                         onset=data_dictionary['session_vars']['onset'],
                         duration=data_dictionary['session_vars']['duration'],
                         trial_type='task')
        

        """ SHOW FIXATION """
        # show inter-stimulus fixation cross
        Projector.show_fixation_cross(dictionary=data_dictionary, screen=screen)
        
        pygame.display.flip()

        # get time to sleep (ISI minus the time already taken)
        time.sleep(data_dictionary[f'trial{trial}']['isi'] - (datetime.now() - data_dictionary[f'trial{trial}']['starting_trial_time']).total_seconds())

        """ SHOW TRIAL """
        # run the trial
        data_dictionary = run_trial(stimulus=data_dictionary[f'trial{trial}']['stimulus'], data_dictionary=data_dictionary)

        # clear screen
        Projector.initialize_screen(screen=screen, inter_trial_blit=True)

        Logger.update_score_csv(action="add_to_csv",
                                task="rifg",
                                path_to_csv=data_dictionary['whole_session_data']['score_csv_path'],
                                score=data_dictionary[f'trial{trial}']['result'],
                                tr=int(trial),
                                additional_data=[data_dictionary[f'trial{trial}']['stimulus']])

    """ UPDATE LOG WITH ENDING INFORMATION"""    
    add_to_event_csv(event_csv_path=data_dictionary['whole_session_data']['event_csv_path'],
                    onset=data_dictionary['session_vars']['onset'] +  settings.RIFG_TRIAL_DURATION,
                    duration=settings.REST_DURATION,
                    trial_type='rest')
    
    """ DISPLAY ENDING REST """
    Projector.show_fixation_cross_rest(screen=screen) 
    pygame.display.flip()

    Projector.show_end_message(screen=screen, dictionary=data_dictionary)
    pygame.display.flip()
    

except KeyboardInterrupt:
    """ DO QUIT EARLY SEQUENCE """
    Logger.print_and_log(f"--- Esc key pressed ---")

    Logger.update_log(log_name=data_dictionary['whole_session_data']['csvlog_path'], dictionary_to_write=data_dictionary)
    
    add_to_event_csv(event_csv_path=data_dictionary['whole_session_data']['event_csv_path'],
                    onset=data_dictionary['session_vars']['onset']  +  settings.RIFG_TRIAL_DURATION,
                    duration=settings.REST_DURATION,
                    trial_type='rest')
    # print the data dictionary in a more readable way
    print_data_dictionary(data_dictionary)

    Projector.show_end_message(screen=screen, dictionary=data_dictionary)
    pygame.display.flip()



