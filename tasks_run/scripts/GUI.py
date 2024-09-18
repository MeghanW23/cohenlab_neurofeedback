import tkinter as tk
from tkinter import ttk
import os
import subprocess
import re
import matplotlib.pyplot as plt
from PIL import Image, ImageTk

plot_img_dir_path: str = "/Users/meghan/cohenlab_neurofeedback/tasks_run/data/gui_graph_imgs"
nfb_log_dir_path: str = "/Users/meghan/cohenlab_neurofeedback/tasks_run/data/nfb_logs"
rifg_log_dir_path: str = "/Users/meghan/cohenlab_neurofeedback/tasks_run/data/rifg_logs"
data_dictionary: dict = {}
def wait_for_log(func):
    def wrapper(*args, **kwargs):
        global data_dictionary
        global nfb_log_dir_path
        global rifg_log_dir_path

        if "starting_rifg_logs" not in data_dictionary:
            data_dictionary["starting_rifg_logs"] = len(os.listdir(rifg_log_dir_path))
        if "starting_nfb_logs" not in data_dictionary:
            data_dictionary["starting_nfb_logs"] = len(os.listdir(nfb_log_dir_path))

        if data_dictionary["starting_rifg_logs"] != len(os.listdir(rifg_log_dir_path)):
            subtitle.config(text="Running rifg")
            data_dictionary["task"] = "rifg"
            func(*args, **kwargs)

        if data_dictionary["starting_nfb_logs"] != len(os.listdir(nfb_log_dir_path)):
            subtitle.config(text="Running nfb")
            data_dictionary["task"] = "nfb"
            func(*args, **kwargs)

        else:
            func(*args, **kwargs)

        return None

    return wrapper
@wait_for_log
def update_gui():
    global data_dictionary
    if "task" in data_dictionary:
        subtitle.config(text="Task Start Detected...")
        if data_dictionary["task"] == 'nfb':
            track_nfb()
        elif data_dictionary["task"] == 'rifg':
            track_rifg()

    # Schedule the next update
    root.after(1000, update_gui)  # Update every 1000 ms (1 second)
def get_log_file(log_dir_path: str) -> str:
    text_files: list = [os.path.join(log_dir_path, file) for file in os.listdir(log_dir_path) if file.endswith(".txt")]
    most_recent_text_file: str = max(text_files, key=os.path.getmtime)
    return most_recent_text_file
def track_value(shell_command_to_get_string: str, re_pattern: str, match_group: int) -> float:
    result = subprocess.run(shell_command_to_get_string, shell=True, text=True, capture_output=True)

    if result.returncode == 0:
        full_string = result.stdout
    else:
        full_string = result.stderr
    match = re.search(re_pattern, string=full_string)
    if match and 'nan' not in match.group(match_group) and match is not None:
        value: float = float(match.group(match_group))

        return value
def track_nfb():
    subtitle.config(text="Running Neurofeedback")

    nfb_text_file: str = get_log_file(log_dir_path=nfb_log_dir_path)

    nfb_activation_value: float = track_value(shell_command_to_get_string=f"grep 'Normalized Mean Activation' {nfb_text_file} | tail -n 1",
                                              re_pattern=r"Normalized Mean Activation:\s*(nan|-?\d*\.\d+)",
                                              match_group=1)

    if nfb_activation_value is not None and nfb_activation_value != 'nan':
        nfb_update_label.config(text=f"Normalized ROI Activation: {nfb_activation_value}")
        nfb_update_label.pack()

        nfb_progressbar.config(value=(nfb_activation_value * 100))
        nfb_progressbar.pack()

    trial_num = track_value(shell_command_to_get_string=f"grep 'Starting Block' {nfb_text_file} | grep Trial | tail -n 1",
                            re_pattern=r"Starting Block(\d+), Trial (\d+)...",
                            match_group=2)


    if trial_num is not None:
        nfb_trial_label.config(text=f"Trial Number: {int(trial_num)} of 140")
        nfb_trial_label.pack()
        nfb_trial_progressbar.config(value=((trial_num / 140) * 100))
        nfb_trial_progressbar.pack()

        global data_dictionary

        if "nfb_values" not in data_dictionary:
            data_dictionary["nfb_values"]: list = [nfb_activation_value]
        else:
            data_dictionary["nfb_values"].append(nfb_activation_value)

        if "trial_num" not in data_dictionary:
            data_dictionary["trial_num"]: list = [trial_num]
        else:
            data_dictionary["trial_num"].append(trial_num)

        if trial_num < 20 or trial_num > 140:
            nfb_block_type.config(text="Trial Type: Rest")
        else:
            nfb_block_type.config(text="Trial Type: Neurofeedback")

        nfb_block_type.pack(side=tk.BOTTOM)

        plt.close("all")
        path_to_graph_image = plot_value(x_axis=data_dictionary["trial_num"], y_axis=data_dictionary["nfb_values"], x_label="Trials", y_label="NFB_Value", plot_title="NFB Value over Trials", trial_num=int(trial_num))
        graph_image = Image.open(path_to_graph_image)
        resized_graph_image = graph_image.resize((450, 300))
        tk_resized_graph_image = ImageTk.PhotoImage(resized_graph_image)

        tk_resized_nfb_logo_img_label.image = tk_resized_graph_image
        tk_resized_nfb_logo_img_label.config(image=tk_resized_graph_image)
        tk_resized_nfb_logo_img_label.pack()
def track_rifg():
    global rifg_log_dir_path
    subtitle.config(text="Running RIFG Task ...")
    tk_resized_nfb_logo_img_label.destroy()
    log_file: str = get_log_file(log_dir_path=rifg_log_dir_path)
    trial_num: float = track_value(shell_command_to_get_string=f"grep 'Starting Trial' {log_file}",
                                   re_pattern=r" ==== Starting Trial (\d+) ====",
                                   match_group=1
                                   )
    if trial_num is not None:
        rifg_trial_label.config(text=f"Trial: {trial_num}")
        rifg_trial_label.pack()

def plot_value(x_axis: list, y_axis: list, x_label: str, y_label: str, plot_title: str, trial_num: int):
    plt.figure(figsize=(8, 6))
    plt.plot(x_axis, y_axis)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(plot_title)

    path_to_graph_image: str = os.path.join(plot_img_dir_path, f"plot_trial{trial_num}.png")
    older_graph_image: str = os.path.join(plot_img_dir_path, f"plot_trial{trial_num - 1}.png")
    try:
        plt.savefig(path_to_graph_image)
    except Exception as e:
        pass
    if os.path.exists(older_graph_image):
        os.remove(older_graph_image)

    return path_to_graph_image
def stop():
    root.quit()

root = tk.Tk()
title = ttk.Label(root, text="ADHD Stimulants Task Results Visualizer", font=("Times New Roman", 20, "underline"), foreground="black")
title.pack()

subtitle = ttk.Label(root, text="No Scripts Currently Running", font=("Times New Roman", 18), foreground="black")
subtitle.pack()

stop_button = ttk.Button(root, text="Close", command=stop)
stop_button.pack()

nfb_update_label = ttk.Label(root, font=("Times New Roman", 15))
nfb_progressbar = ttk.Progressbar(root, length=200, orient='horizontal', mode='determinate')

nfb_trial_label = ttk.Label(root, font=("Times New Roman", 15))
nfb_trial_progressbar = ttk.Progressbar(root, length=200, orient='horizontal', mode='determinate')

nfb_logo_path = "/Users/meghan/cohenlab_neurofeedback/tasks_run/nfb_materials/logo_for_gui_transparent.png"
nfb_logo_img = Image.open(nfb_logo_path)
resized_nfb_logo_img = nfb_logo_img.resize((450, 300))
tk_resized_nfb_logo_img = ImageTk.PhotoImage(resized_nfb_logo_img)
tk_resized_nfb_logo_img_label = tk.Label(root, image=tk_resized_nfb_logo_img)
tk_resized_nfb_logo_img_label.pack()


rifg_trial_label = ttk.Label(root, font=("Times New Roman", 15))

nfb_block_type = ttk.Label(root, font=("Times New Roman", 15))
update_gui()

root.mainloop()
