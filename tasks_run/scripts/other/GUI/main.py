import os
import sys
from FilesystemGUI2 import FileSystemGUI
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def stop():
    sys.exit(1)

root = tk.Tk() # initialize root window
chid: str = os.getenv("CHID")
if chid is None:
    print(f"Could not get valid value for environment variable: CHID")
    sys.exit(1)

fs: FileSystemGUI = FileSystemGUI(root=root,
                                  hostname="e3-login.tch.harvard.edu",
                                  username=chid,
                                  path_to_key=f"/workdir/.ssh/docker_e3_key_{chid}",
                                  remote_start_path="/lab-share/Neuro-Cohen-e2/Public/projects/ADHD_NFB/")
# make title widget
title: tk.Label = ttk.Label(root, text="ADHD Project Container", font=("Times New Roman", 20, "underline"), foreground="black")
title.pack()

# make subtitle widget
subtitle: tk.Label = ttk.Label(root, text="No Scripts Currently Running", font=("Times New Roman", 18), foreground="black")
subtitle.pack()

# nfb logo widget
nfb_logo_path: str = "/workdir/tasks_run/nfb_materials/logo_for_gui_transparent.png"
nfb_logo_img: Image = Image.open(nfb_logo_path)
resized_nfb_logo_img: Image = nfb_logo_img.resize((450, 300))
tk_resized_nfb_logo_img: ImageTk.PhotoImage = ImageTk.PhotoImage(resized_nfb_logo_img)
tk_resized_nfb_logo_img_label: tk.Label= tk.Label(root, image=tk_resized_nfb_logo_img)
tk_resized_nfb_logo_img_label.pack()

msit_button: ttk.Button = ttk.Button(root, text="Run MSIT Task", command=stop, width=30)
msit_button.pack(pady=5)

rifg_button: ttk.Button = ttk.Button(root, text="Run RIFG Task", command=stop, width=30)
rifg_button.pack(pady=5)

nfb_button: ttk.Button = ttk.Button(root, text="Run NFB Task", command=stop, width=30)
nfb_button.pack(pady=5)

rest_button: ttk.Button = ttk.Button(root, text="Run Rest Task", command=stop, width=30)
rest_button.pack(pady=5)

localizer_button: ttk.Button = ttk.Button(root, text="Run Localizer", command=stop, width=30)
localizer_button.pack(pady=5)

e3_button: ttk.Button = ttk.Button(root, text="Push or Pull from E3", command=fs.run, width=30)
e3_button.pack(pady=5)

stop_button: ttk.Button = ttk.Button(root, text="Exit", command=stop)
stop_button.pack(pady=5)

root.mainloop()
