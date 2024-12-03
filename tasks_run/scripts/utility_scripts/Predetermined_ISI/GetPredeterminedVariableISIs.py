import sys
import os
import random
import csv
from datetime import datetime

def add_to_csv(pre_ISIs: list[int], post_ISIs: list[int]):
    now = datetime.now()
    formatted_timestamp = now.strftime("%Y_%m_%d")
    csv_filename = f"RIFG_predetermined_ISIs_{formatted_timestamp}.csv"
    path_to_csv = os.path.join(settings.PREDETERMINED_ISI_MAKER_DIR, csv_filename)

    with open(path_to_csv, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["index", "pre_ISIs", "post_ISIs"])
        index = 0
        for preISI, postISI in zip(pre_ISIs, post_ISIs):
            index += 1
            writer.writerow([index, preISI, postISI])

def get_random_ISIs() -> list[float]:
    ISI_list: list[float] = []
    # range() only accepts integer arguments, so make the float vals into ints
    min_val = int(settings.ISI_MIN * 100)
    max_val = int(settings.ISI_MAX * 100)
    step_val = int(settings.ISI_STEP * 100)
    for _ in range(1, settings.RIFG_N_TRIALS + 1):
        random_ISI: float = random.choice(range(min_val, max_val + step_val, step_val)) / 100.0
        ISI_list.append(random_ISI)
    return ISI_list

def create_csv(ISI_list: list[float], task: str):

    now = datetime.now()
    formatted_timestamp = now.strftime("%Y_%m_%d")
    csv_filename = f"{task}_event_csv_{formatted_timestamp}.csv"
    path_to_csv = os.path.join(settings.PREDETERMINED_ISI_MAKER_DIR, csv_filename)

    with open(path_to_csv, mode="w", newline="") as f:
        # set csv writer and write headers 
        writer = csv.writer(f)
        writer.writerow(["onset", "duration", "trial_type"])
        
        # write starting-task rest values 
        starting_onset: float = 0
        starting_duration: float = settings.REST_DURATION
        starting_task = "rest"
        writer.writerow([starting_onset, starting_duration, starting_task])

        trial_specific_onset = starting_duration
        for ISI in ISI_list:
            # get this trial's values 
            duration = settings.RIFG_TRIAL_DURATION
            trial_type = "task"
            onset = trial_specific_onset

            # write to a CSV 
            writer.writerow([onset, duration, trial_type])

            # update values for next trial
            trial_specific_onset = trial_specific_onset + duration + ISI
        
        ending_onset: float = trial_specific_onset
        ending_duration: float = settings.REST_DURATION
        ending_task: float = "rest"
        writer.writerow([ending_onset, ending_duration, ending_task])
        
# get parameters from settings 
script_dir_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if not os.path.exists(script_dir_path):
    print(f"Could not find path: {script_dir_path}")
    sys.exit(1)
else:
    sys.path.append(script_dir_path)

import settings

# make preRIFG csv 
create_csv(ISI_list=get_random_ISIs(),
           task="preRIFG")

# make postRIFG csv 
create_csv(ISI_list=get_random_ISIs(),
           task="postRIFG")