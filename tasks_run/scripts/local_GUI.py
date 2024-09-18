import tkinter as tk
from tkinter import ttk
import threading
import time
import os
import re
import sys
from PIL import Image, ImageTk

def get_most_recent_log(first_trial: bool) -> str:
    output_log_dir = "/workdir/tasks_run/data/nfb_logs"
    starting_file_count: int = len(os.listdir(output_log_dir))
    if first_trial:
        while True:
                current_file_count: int = len(os.listdir(output_log_dir))
                if current_file_count != starting_file_count:
                    break

    file_list = [os.path.join(output_log_dir, file) for file in os.listdir(output_log_dir) if file.endswith(".txt")]

    if not file_list:
        print("No log files found.")
        sys.exit(1)

    most_recent_file = max(file_list, key=os.path.getmtime)

    return most_recent_file
def get_trial(input_log: str, previous_trials: list):
    while True:
        with open(input_log, 'r') as file:
            for line in reversed(file.readlines()):
                pattern = r'Starting Block(\d+), Trial (\d+)...'
                match = re.search(pattern, line)
                if match:
                    trial = int(match.group(2))
                    previous_trials.append(trial)
                    return trial, previous_trials
        time.sleep(1)
def get_nfb_score(input_log: str, previous_scores: list):
    while True:
        with open(input_log, 'r') as file:
            for line in reversed(file.readlines()):
                pattern = r"Normalized Mean Activation: (-?\d+\.\d+)"
                match = re.search(pattern, line)
                if match:
                    nfb_score = match.group(1)
                    if float(nfb_score) not in previous_scores:
                        previous_scores.append(float(nfb_score))
                    return float(nfb_score), previous_scores
            else:
                time.sleep(0.1)
def normalize(value, old_min=-1, old_max=1, new_min=0, new_max=100):
    return ((value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min
def update_progress():
    previous_trials = []
    previous_scores = []
    while True:
        if not previous_trials:
            root.after(0, lambda: label.config(text=f"Starting Neurofeedback ..."))
        root.after(0, lambda: image_label.destroy())
        root.after(0, lambda: button.destroy())


        progressbar = ttk.Progressbar(root, orient='horizontal', length=250, mode='determinate')
        canvas.create_window(400, 250, window=progressbar)
        # progressbar.grid(row=0, column=2, padx=20)

        progress_label = ttk.Label(root, text="Block Progress: ", font=("Comic Sans MS", 20), foreground="black")
        canvas.create_window(125, 250, window=progress_label)
        # progress_label.grid(row=0, column=1, padx=(20, 5))

        nfbprogressbar = ttk.Progressbar(canvas, orient='horizontal', length=250, mode='determinate')
        # nfbprogressbar.grid(row=1, column=2, padx=20)
        canvas.create_window(400, 150, window=nfbprogressbar)


        nfb_progress_label = ttk.Label(canvas, text="NFB Score: ", font=("Comic Sans MS", 20), foreground="black")
        # nfb_progress_label.grid(row=1, column=1, padx=(20, 5))
        canvas.create_window(100, 150, window=nfb_progress_label)



        if not previous_trials:
            most_recent_file = get_most_recent_log(first_trial=True)
        else:
            most_recent_file = get_most_recent_log(first_trial=False)

        this_trial, previous_trials = get_trial(input_log=most_recent_file, previous_trials=previous_trials)
        nfb_score, previous_scores = get_nfb_score(input_log=most_recent_file, previous_scores=previous_scores)

        # Ensure the update happens on the main thread
        if this_trial is not None:
            root.after(0, progressbar.config(value=(this_trial / 140) * 100))
            if nfb_score is not None:
                root.after(0, nfbprogressbar.config(value=normalize(nfb_score)))
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

title = ttk.Label(canvas, text="ADHD Stimulants Task Results Visualizer", font=("Comic Sans MS", 20, "underline"), foreground="black")
canvas.create_window(300, 30, window=title)  # Centered in the middle of the canvas

label = ttk.Label(canvas, text="No Scripts Currently Running", font=("Comic Sans MS", 15), foreground="black")
canvas.create_window(300, 68, window=label)  # Centered in the middle of the canvas

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
