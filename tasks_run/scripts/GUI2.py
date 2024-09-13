import sys
import time
from tkinter import *
from tkinter.ttk import *
import Logger
from tkinter import font

class NeurofeedbackGraphicalInterface:
    def __init__(self, master, dictionary):
        self.master = master
        self.master.title("NFB GUI")
        self.dictionary = dictionary

        title = Label(master, text="Neurofeedback Stats and Errors.", font=("Times New Roman", 24, "bold", "underline"))
        title.grid(row=0, column=0, padx=20, pady=10)

        if "output_text_logfile_path" in dictionary["whole_session_data"]:
            log_path: str = self.dictionary["whole_session_data"]["output_text_logfile_path"]
            Logger.print_and_log(f"GUI Reading from Output File: {log_path}")

        else:
            Logger.print_and_log(f"GUI Could not find log path in data dictionary")
            print(dictionary)
            sys.exit(1)

