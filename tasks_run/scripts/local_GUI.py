import tkinter as tk
from tkinter import ttk
import threading
import time
import os
import re
import sys
import subprocess

def get_most_recent_log() -> str:
    output_log_dir = "/Users/meghan/cohenlab_neurofeedback/tasks_run/data/rifg_logs"
    file_list = [os.path.join(output_log_dir, file) for file in os.listdir(output_log_dir) if file.endswith(".txt")]

    if not file_list:
        print("No log files found.")
        sys.exit(1)

    most_recent_file = max(file_list, key=os.path.getmtime)
    print(f"Using Log: {most_recent_file}")

    return most_recent_file


def get_trial(input_log: str) -> int:
    with open(input_log, 'r') as file:
        for line in reversed(file.readlines()):
            pattern = r'Starting Trial (\d+)'
            match = re.search(pattern, line)
            if match:
                print("Found line:")
                print(match.group(1))
                trial = int(match.group(1))
                return trial

    print("Found No Trials using Re")
    sys.exit(1)

def update_progress():
    # Disable the button while updating
    button.config(state=tk.DISABLED)

    while True:
        most_recent_file = get_most_recent_log()
        this_trial = get_trial(most_recent_file)

        # Ensure the update happens on the main thread
        root.after(0, lambda: progressbar.config(value=(this_trial / 140) * 100))

        time.sleep(1)  # Check for updates every 5 seconds

    # Re-enable the button
    button.config(state=tk.NORMAL)

# Setup Tkinter GUI
root = tk.Tk()
progressbar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
progressbar.grid(row=0, column=0)

button = ttk.Button(root, text="Get Session Info", command=update_progress)
button.grid(row=1, column=0)

root.mainloop()
