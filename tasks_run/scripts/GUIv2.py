import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import filedialog
import treeviewexample


def stop():
    root.quit()

root = tk.Tk()
app = treeviewexample.GetFileSystemGUI(root=root,
                                       hostname="e3-login.tch.harvard.edu",
                                       username="ch246081",
                                       path_to_key="/workdir/.ssh/docker_e3_key_ch246081",
                                       remote_start_path="/lab-share/Neuro-Cohen-e2/Public/projects/ADHD_NFB")

title = ttk.Label(root, text="ADHD Project Container", font=("Times New Roman", 20, "underline"), foreground="black")
title.pack()

subtitle = ttk.Label(root, text="No Scripts Currently Running", font=("Times New Roman", 18), foreground="black")
subtitle.pack()

nfb_logo_path = "/workdir/tasks_run/nfb_materials/logo_for_gui_transparent.png"
nfb_logo_img = Image.open(nfb_logo_path)
resized_nfb_logo_img = nfb_logo_img.resize((450, 300))
tk_resized_nfb_logo_img = ImageTk.PhotoImage(resized_nfb_logo_img)
tk_resized_nfb_logo_img_label = tk.Label(root, image=tk_resized_nfb_logo_img)
tk_resized_nfb_logo_img_label.pack()

msit_button = ttk.Button(root, text="Run MSIT Task", command=stop, width=20)
msit_button.pack()

rifg_button = ttk.Button(root, text="Run RIFG Task", command=stop, width=20)
rifg_button.pack()

nfb_button = ttk.Button(root, text="Run NFB Task", command=stop, width=20)
nfb_button.pack()

rest_button = ttk.Button(root, text="Run Rest Task", command=stop, width=20)
rest_button.pack()

localizer_button = ttk.Button(root, text="Run Localizer", command=stop, width=20)
localizer_button.pack()

e3_button = ttk.Button(root, text="Push or Pull from E3", command=app.run, width=20)
e3_button.pack()

stop_button = ttk.Button(root, text="Exit", command=stop)
stop_button.pack()

root.mainloop()
