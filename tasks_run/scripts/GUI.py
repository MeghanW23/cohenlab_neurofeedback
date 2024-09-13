from tkinter import *
from tkinter.ttk import *
import random
import time
def start_nfb(trial, n_trials):
    for trial in range(1, n_trials + 1):
        bar["value"] = random.randint(0, 100)
        time.sleep(1)
        bar.update_idletasks()

root = Tk()
root.geometry("800x600+100+50")  # 800x600 window positioned at (100, 50)
bar = Progressbar(root, orient=HORIZONTAL, length=300)
bar.pack(padx=10)
bar.pack(pady=10)

Button(root, text="start_nfb", command=start_nfb(trial=1, n_trials=140)).pack()

root.mainloop()