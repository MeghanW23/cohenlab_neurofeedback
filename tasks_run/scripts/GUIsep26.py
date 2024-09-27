import os.path
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import subprocess
import settings
from tkinter import messagebox

def stop():
    root.quit()

def run_rifg():
    try:
        subprocess.run(["python", os.path.join("/workdir/tasks_run/scripts", settings.RIFG_SCRIPT_NAME)])
    except Exception as e:
        messagebox.showwarning("FATAL SCRIPT ERROR", str(e))
    else:
        messagebox.showinfo("Script Ended", f"Script: {settings.RIFG_SCRIPT_NAME} has ended")


root = tk.Tk()
title = ttk.Label(root, text="ADHD Stimulants Task Results Visualizer", font=("Times New Roman", 20, "underline"), foreground="black")
title.pack(padx=5, pady=5)

subtitle = ttk.Label(root, text="No Scripts Currently Running", font=("Times New Roman", 18), foreground="black")
subtitle.pack()

nfb_logo_path = "/workdir/tasks_run/nfb_materials/logo_for_gui_transparent.png"
nfb_logo_img = Image.open(nfb_logo_path)
resized_nfb_logo_img = nfb_logo_img.resize((450, 300))
tk_resized_nfb_logo_img = ImageTk.PhotoImage(resized_nfb_logo_img)
tk_resized_nfb_logo_img_label = tk.Label(root, image=tk_resized_nfb_logo_img)
tk_resized_nfb_logo_img_label.pack()

start_rifg_button = ttk.Button(root, text="Start rIFG Task", command=run_rifg)
start_rifg_button.pack()

stop_button = ttk.Button(root, text="Close", command=stop)
stop_button.pack()



root.mainloop()
