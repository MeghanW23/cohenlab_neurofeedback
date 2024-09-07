import sys
from typing import Optional, Union, Tuple
import time
import pprint
from datetime import datetime, timedelta

# Re-Writing the Calculation Script
print("Script for Calculating ROI Activation from Dicoms")

""" FUNCTIONS """


def get_most_recent(item: str) -> str:
    if item == 'mask':
        print("Getting Most Recent Mask")

    elif item == "dicom_dir":
        print("Getting Most Recent Dicom Directory")

    else:
        print("Please enter a valid 'item' param for get_most_recent_item()")
        print(f"{str(item)} is not a valid parameter")
        sys.exit(1)

    return item


def create_output_log(action: str) -> Optional[str]:
    if action == "create":
        output_log_path: str = "/path/to/output/log"
        print("Created Output Log")

        return output_log_path

    elif action == "update":
        output_log_path: str = "/path/to/output/log"
        print("Updated Output Log")

    else:
        print("Please enter a valid 'action' param for create_output_log()")
        print(f"{str(action)} is not a valid parameter")
        sys.exit(1)


def print_pretty_dictionary(dictionary: dict) -> None:
    pprint.pprint(dictionary, indent=4)


def get_time(action: str, time1: datetime = None, time2: Union[str, datetime] = None) -> Union[datetime, timedelta]:
    if action == "get_time":
        # Get Script Start Time
        now: datetime = datetime.now()
        return now

    elif action == "subtract_two_times":
        if time1 is None or time2 is None:
            print("In order to subtract two times using get_time(), you must input a time for params: time1 and time2")

        else:
            if time2 == "now":
                now: datetime = datetime.now()
                total_time: timedelta = now - time1

                return total_time

            else:
                total_time: timedelta = time2 - time1
                return total_time

    else:
        print("Input for Param: 'action' in func 'get_time' is not a valid option")
        sys.exit(1)


def get_new_block(dictionary: dict) -> dict:
    if "current_block" not in dictionary["whole_session_dictionary"]:
        dictionary["whole_session_dictionary"]["current_block"]: int = dictionary["whole_session_dictionary"][
            "starting_block"]

    else:
        dictionary["whole_session_dictionary"]["old_blocks"]: int = dictionary["whole_session_dictionary"][
            "current_block"]
        dictionary["whole_session_dictionary"]["current_block"]: int = dictionary["whole_session_dictionary"][
                                                                           "current_block"] + 1

    return dictionary


def inter_trial_error_handler(dictionary: dict, trial: int, successful_iteration: bool) -> Tuple[dict, bool, bool]:
    TrialDict: dict = dictionary[f"trial{trial}"]

    if successful_iteration:
        # if there were no issues at all with this trial, just update to say it was an error free trial
        if "error_free_trial" not in dictionary:
            TrialDict["error_free_trial"]: bool = True
        else:
            # if there were issues with this trial, but was able to finish with a successful iteration, record resolving error
            TrialDict["error_resolved"]: bool = True

        RunningThisTrial = False  # End Trial
        RunningThisBlock = True  # Don't End Block
        return dictionary, RunningThisTrial, RunningThisBlock

    else:
        TrialDict["error_free_trial"]: bool = False

        if "trial_error_counter" not in TrialDict:
            TrialDict["trial_error_counter"]: int = 1
        else:
            TrialDict["trial_error_counter"] += 1

        if TrialDict["trial_error_counter"] >= 3:

            print("Max Trial Errors Reached")
            print(f"error count: {TrialDict['trial_error_counter']}")
            return close_block(dictionary=dictionary, ending_due_to_error=True)
        else:

            print(f"error count: {TrialDict['trial_error_counter']}")
            RunningThisTrial = True
            RunningThisBlock = True

            return dictionary, RunningThisTrial, RunningThisBlock


def close_block(dictionary: dict, ending_due_to_error: bool = False) -> Tuple[dict, bool, bool]:
    dictionary["whole_session_dictionary"]["ending_block_time"]: datetime = get_time(action="get_time")
    dictionary["whole_session_dictionary"]["total_block_time"]: timedelta = get_time(action="subtract_two_times",
                                                                                     time1=dictionary[
                                                                                         "whole_session_dictionary"][
                                                                                         "starting_block_time"],
                                                                                     time2=dictionary[
                                                                                         "whole_session_dictionary"][
                                                                                         "ending_block_time"])

    if ending_due_to_error:
        dictionary["whole_session_dictionary"]["ending_block_due_to_error"]: bool = True
        print("Ending Block Due To Errors.")

    else:
        dictionary["whole_session_dictionary"]["ending_block_due_to_error"]: bool = False
        print(
            f"All {DataDictionary['whole_session_dictionary']['n_trials_in_block']} Trials are Done. Starting the Next Block Now ...")

    RunningThisTrial: bool = False
    RunningThisBlock: bool = False

    return dictionary, RunningThisTrial, RunningThisBlock


# Do Starting Session Actions
DataDictionary: dict = {
    "whole_session_dictionary": {}}  # create data dictionary, then create sub-dictionary for whole session data
DataDictionary["whole_session_dictionary"]["starting_script_time"]: datetime = get_time(action="get_time")
DataDictionary["whole_session_dictionary"]["roi_mask"]: str = get_most_recent(item='mask')
DataDictionary["whole_session_dictionary"]["dicom_dir"]: str = get_most_recent(item='dicom_dir')
DataDictionary["whole_session_dictionary"]["output_log_path"]: str = create_output_log(action="create")
DataDictionary["whole_session_dictionary"]["starting_block"]: int = 1
DataDictionary["whole_session_dictionary"]["n_trials_in_block"]: int = 20

RunningThisSession: bool = True
while RunningThisSession:
    """ Setup Block """
    DataDictionary = get_new_block(dictionary=DataDictionary)
    DataDictionary["whole_session_dictionary"]["starting_block_time"]: datetime = get_time(action="get_time")
    trial: int = 1  # Initialize trial counting variable

    RunningThisBlock: bool = True
    while RunningThisBlock:

        RunningThisTrial: bool = True
        while RunningThisTrial:
            # create trial dictionary, add trial starting time
            if f"trial{trial}" not in DataDictionary:
                DataDictionary[f"trial{trial}"]: dict = {}
                DataDictionary[f"trial{trial}"]["starting_time"]: datetime = get_time(action="get_time")
                print(f"Starting Block {DataDictionary['whole_session_dictionary']['current_block']}, Trial {trial},")
            else:
                print(f"Repeating Block {DataDictionary['whole_session_dictionary']['current_block']}, Trial {trial},")
            TrialDict = DataDictionary[f"trial{trial}"]

            # Run Trial
            try:
                time.sleep(0.5)

                if trial % 3 == 0:
                    raise Exception

                # close error-free trial
                DataDictionary, RunningThisTrial, RunningThisBlock = inter_trial_error_handler(
                    dictionary=DataDictionary, trial=trial, successful_iteration=True)

            except Exception as e:
                print("----")
                print("An Error Has Occurred: ")
                print(e)
                print("----")
                DataDictionary, RunningThisTrial, RunningThisBlock = inter_trial_error_handler(
                    dictionary=DataDictionary, trial=trial, successful_iteration=False)

            # End The Trial

            # get ending trial time
            TrialDict["ending_time"]: datetime = get_time(action="get_time")
            TrialDict["total_trial_time"]: timedelta = get_time(action="subtract_two_times",
                                                                time1=TrialDict["starting_time"],
                                                                time2=TrialDict["ending_time"])

            # if restarting block
            if not RunningThisTrial and not RunningThisBlock:
                print("Starting New Block")

            # if starting next trial
            elif not RunningThisTrial:
                trial = trial + 1  # get new trial number

            # if re-starting trial
            else:
                print(f"Repeating trial: {trial}")

            # if we just ran the last trial
            if trial > DataDictionary['whole_session_dictionary']['n_trials_in_block']:
                DataDictionary, RunningThisBlock, RunningThisTrial = close_block(dictionary=DataDictionary,
                                                                                 ending_due_to_error=False)

