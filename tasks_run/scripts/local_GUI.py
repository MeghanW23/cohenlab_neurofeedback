import tkinter as tk
from tkinter import ttk
import threading
import time
import os
import re
import sys
from typing import Union
from PIL import Image, ImageTk

def get_most_recent_log() -> str:
    output_log_dir = "/Users/meghan/cohenlab_neurofeedback/tasks_run/data/rifg_logs"
    file_list = [os.path.join(output_log_dir, file) for file in os.listdir(output_log_dir) if file.endswith(".txt")]

    if not file_list:
        print("No log files found.")
        sys.exit(1)

    most_recent_file = max(file_list, key=os.path.getmtime)

    return most_recent_file


def get_trial(input_log: str, previous_trials: list):
    with open(input_log, 'r') as file:
        for line in reversed(file.readlines()):
            pattern = r'Starting Trial (\d+)'
            match = re.search(pattern, line)
            if match and match not in previous_trials:
                trial = int(match.group(1))
                previous_trials.append(trial)
                return trial, previous_trials

    print("Found No Trials using Re")
    return None

def get_nfb_score(input_log:str, previous_trials):
    with open(input_log, 'r') as file:
        for line in reversed(file.readlines()):
            pattern = r'Normalized Mean Activation: (\d+)'
            match = re.search(pattern, line)
            if match:
                nfb_score = match.group(1)

def update_progress():
    previous_trials = []
    while True:
        root.after(0, lambda: image_label.destroy())
        root.after(0, lambda: button.destroy())
        root.after(0, lambda: stop_button.destroy())

        progressbar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
        progressbar.grid(row=0, column=2, padx=20)

        progress_label = ttk.Label(root, text="Block Progress: ", font=("Comic Sans MS", 20), foreground="black")
        progress_label.grid(row=0, column=1, padx=(20, 5))


        most_recent_file = get_most_recent_log()
        this_trial, previous_trials = get_trial(most_recent_file, previous_trials)

        # Ensure the update happens on the main thread
        if this_trial is not None:
            root.after(0, progressbar.config(value=(this_trial / 140) * 100))
            root.after(0, lambda: label.config(text=f"Running Trial {this_trial} of 140"))



        time.sleep(0.1)
def start_thread():
    thread = threading.Thread(target=update_progress, daemon=True)
    thread.start()

def stop():
    sys.exit(1)

# Setup Tkinter GUI
root = tk.Tk()
# Create a canvas with a horizontal line
canvas = tk.Canvas(root, width=600, height=400, highlightthickness=1)
canvas.grid(row=0, column=0, columnspan=3, padx=5, pady=5)
rectangle_id = canvas.create_rectangle(1, 1, 600, 400, outline="black", width=5)

title = ttk.Label(canvas, text="ADHD Stimulants Task Results Visualizer", font=("Comic Sans MS", 30, "underline"), foreground="black")
canvas.create_window(300, 30, window=title)  # Centered in the middle of the canvas

label = ttk.Label(canvas, text="No Scripts Currently Running", font=("Comic Sans MS", 20), foreground="black")
canvas.create_window(300, 65, window=label)  # Centered in the middle of the canvas

# canvas.create_rectangle(100, 100, 500, 350, outline="white", fill="white")
# Load an image using Pillow
image_path = "/workdir/tasks_run/nfb_materials/logo_for_gui_transparent.png"
image = Image.open(image_path)
resized_image = image.resize((450, 300))

# Convert the image to a Tkinter-compatible format
tk_image = ImageTk.PhotoImage(resized_image)

# Create a label to hold the image
image_label = tk.Label(canvas, image=tk_image)
canvas.create_window(300, 240, window=image_label)  # Centered in the middle of the canvas

style = ttk.Style()
style.configure("TButton", background="white", foreground="black", font=("Comic Sans MS", 18))
button = ttk.Button(root, text="Start RIFG GUI", command=start_thread)
button.grid(row=1, column=0, columnspan=2, pady=(0, 5))


stop_button = ttk.Button(root, text="Close", command=stop)
stop_button.grid(row=1, column=1, columnspan=2, pady=(0, 5))

root.mainloop()
