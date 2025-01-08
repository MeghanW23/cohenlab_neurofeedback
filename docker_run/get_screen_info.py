from AppKit import NSScreen
import sys
import os
import csv
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Import settings
path_to_settings_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tasks_run/scripts/")
sys.path.append(path_to_settings_dir)
import settings

# Get screens and make a dictionary to hold monitor information produced
screens = NSScreen.screens()
monitor_information: dict = {}
monitor_to_use = 1  # Default to the second monitor

# Get information for each screen
for screen_num, screen in enumerate(screens, start=1):
    # Get frame and visible frame
    frame = screen.frame()  # Correctly call the frame() method
    visible_frame = screen.visibleFrame()  # Visible frame

    # Add monitor information to a dictionary
    monitor_information[f"screen_{screen_num}"] = {
        "resolution_width": frame.size.width,
        "resolution_height": frame.size.height,
        "x_offset": frame.origin.x,  # X offset
        "y_offset": frame.origin.y,  # Y offset
        "visible_width": visible_frame.size.width,
        "visible_height": visible_frame.size.height,
        "scale_factor": screen.backingScaleFactor()
    }

    # Create CSV headers during the first iteration
    if screen_num == 1:
        with open(settings.MONITOR_INFO_CSV_PATH, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["monitor_number"] + list(monitor_information[f"screen_{screen_num}"].keys()))
    else:
        monitor_to_use = 2  # Use the second monitor

    # Add monitor information as a row in the CSV
    with open(settings.MONITOR_INFO_CSV_PATH, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([screen_num] + list(monitor_information[f"screen_{screen_num}"].values()))

# Output information for the selected monitor (default to second)
selected_monitor = monitor_information[f'screen_{monitor_to_use}']
print(f"Using Target Monitor Width: {int(selected_monitor['resolution_width'])}")
print(f"Using Target Monitor Height: {int(selected_monitor['resolution_height'])}")
print(f"Using Target Monitor X Offset: {int(selected_monitor['x_offset'])}")
print(f"Using Target Monitor Y Offset: {int(selected_monitor['y_offset'])}")