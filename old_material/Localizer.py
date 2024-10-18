import sys
import pandas as pd
import ScriptManager
import Logger
import settings

print("---------------")
print("\nPlease ensure the following conditions are met before running this script: \n")
print("1. You have already run a registration script to put an MNI space mask into subject space.")
print("2. Your localizer task has finished completely.\n")
print("---------------")
start_script: str = input("Type 'y' if conditions are met: ")
if start_script == "y":
    print("Ok, starting script ...")
else:
    print("Ok Ending script now. ")
    sys.exit(0)

# get pid
pid = ScriptManager.get_participant_id()
# create output log
Logger.create_log(filetype=".txt", log_name=f"{pid}_localization_log")

# get event file
choose_task = ""
while True:
    choose_task = input("Did you run task: MSIT or RIFG (m/r): ")
    if choose_task == "m":
        Logger.print_and_log("OK, Using MSIT Event CSV")
        event_csv = pd.read_csv(settings.MSIT_EVENT_CSV, delimiter=",")
        break

    elif choose_task == "r":
        Logger.print_and_log("OK, Using RIFG Event CSV")
        event_csv = pd.read_csv(settings.RIFG_EVENT_CSV, delimiter=",")
        break

    else:
        Logger.print_and_log("Please choose either 'r' or 'm'.")

