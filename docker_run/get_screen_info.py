from AppKit import NSScreen
import sys
import os
import csv
import warnings
warnings.filterwarnings("ignore", category=UserWarning) # to ignore any settings warnings
path_to_settings_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tasks_run/scripts/")
sys.path.append(path_to_settings_dir)
import settings

# get screens and make a dictionary to hold monitor information produced
screens = NSScreen.screens()
monitor_information: dict = {}
monitor_to_use = 1
# get information for each screen
for screen_num, screen in enumerate(screens, start=1):
    
    # add monitor information to a dictionary
    monitor_information[f"screen_{screen_num}"] = {
        "frame_size": screen.frame().size,
        "resolution_width": screen.frame().size.width,
        "resolution_height": screen.frame().size.height,
        "visible_area": screen.visibleFrame().size,
        "scale_factor": screen.backingScaleFactor()
    }

    # make csv and add headers if its the first for loop iteration
    if screen_num == 1:
        with open(settings.MONITOR_INFO_CSV_PATH, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["monitor_number"] + list(monitor_information[f"screen_{screen_num}"].keys()))
    else:
        monitor_to_use = 2
    # add monitor information as a row in the csv
    with open(settings.MONITOR_INFO_CSV_PATH, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([screen_num] + list(monitor_information[f"screen_{screen_num}"].values()))

print(f"Using Target Monitor Width: {int(monitor_information[f'screen_{monitor_to_use}']['resolution_width'])}")
print(f"Using Target Monitor Height: {int(monitor_information[f'screen_{monitor_to_use}']['resolution_height'])}")