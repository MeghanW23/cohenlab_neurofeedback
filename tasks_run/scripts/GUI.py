import sys
from tkinter import *
from tkinter.ttk import *
import subprocess
import sys
def start_neurofeedback():
    label.config(text="Running Neurofeedback")
    root.update_idletasks()
    subprocess.run(["python", "/workdir/tasks_run/scripts/nf_calc_MW.py"])
    print("Script Done, Closing GUI")
    sys.exit(1)

def start_rifg():
    label.config(text="Running RIFG")
    root.update_idletasks()
    subprocess.run(["python", "/workdir/tasks_run/scripts/rifg_task.py"])
    print("Script Done, Closing GUI")
    sys.exit(1)


root = Tk()
nf_button = Button(root, text="Start Neurofeedback", command=start_neurofeedback)
nf_button.grid(row=0, column=0, pady=5, padx=5)

rifg_button = Button(root, text="Start RIFG Task", command=start_rifg)
rifg_button.grid(row=1, column=0, pady=5)

label = Label(root, text="Nothing is Running Yet.")
label.grid(row=2, column=0, pady=5)

root.mainloop()