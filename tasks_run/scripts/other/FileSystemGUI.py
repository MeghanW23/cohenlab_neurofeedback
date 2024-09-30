import os.path
import subprocess

import paramiko
import tkinter as tk
from tkinter import ttk
import sys
from tkinter import messagebox
import traceback
from tkinter import filedialog

class GetFileSystemGUI:
    def __init__(self, root, hostname, username, path_to_key, remote_start_path):
        self.root = root
        self.hostname = hostname
        self.username = username
        self.path_to_key = path_to_key
        self.remote_start_path = remote_start_path
        self.tree_window = None
    def open_tree_window(self):
        if self.tree_window is None or not self.tree_window.winfo_exists():
            self.tree_window = tk.Toplevel(self.root)
            self.tree_window.title("E3 File Transfer")
            self.tree_window.geometry("800x500")

            self.loading_label = ttk.Label(self.tree_window, text="Please Wait, Connecting to Remote Client ...", font=("Helvetica", 20))
            self.loading_label.pack()             # Create the loading label


            self.tree = ttk.Treeview(self.tree_window, show="tree")
            self.tree.pack(fill=tk.BOTH, expand=True)

            self.close_button = ttk.Button(self.tree_window, text="Close", command=self.stop)
            self.close_button.pack(pady=5)

            self.root.after(100, self.connect_to_remote)
    def connect_to_remote(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(hostname=self.hostname, username=self.username, key_filename=self.path_to_key)
            stdin, stdout, stderr = ssh.exec_command(f"python {self.remote_start_path}/test_file.py")  # Retrieve detailed file list
            self.file_list = stdout.read().decode().strip().splitlines()

            error_message = stderr.read().decode()
            if error_message:
                messagebox.showerror("Error:", error_message) # Print errors if any
                sys.exit(1)
            if not self.file_list:
                messagebox.showerror("Error","No files found.")  # Handle case with no files
                sys.exit(1)

            self_treestruct = self.parse_data(data=self.file_list)
            self.populate_treeview(tree=self.tree, structure=self_treestruct)

            ssh.close()
            self.loading_label.config(text="Please Select Path to Remote Client")

            self.select_button = ttk.Button(self.tree_window, text="Select", command=self.on_item_selected)
            self.select_button.pack(pady=5)

        except Exception as e:
            print(f"Connection failed: {str(e)}")
            traceback.print_exc()  # This will print the traceback to the console
            self.loading_label.config(text="Connection failed!")
    def on_item_selected(self):
        if self.tree.selection():  # Check if any item is selected
            selected_item = self.tree.selection()[0]  # Get the selected item
            item_name = self.tree.item(selected_item, "text")  # Get the filename
            full_path = selected_item  # The iid is set to the full path during insertion

            print(f"Selected Item Name: {item_name}")  # Print the selected item name
            self.loading_label.config(text=f"Selected: {item_name}")
    def parse_data(self, data):
        tree_structure = {}
        for line in data:
            if line.startswith("directory:"):
                path = line.split(": ")[1]
                tree_structure[path] = []
            elif line.startswith("file:"):
                path = line.split(": ")[1]
                directory = "/".join(path.split("/")[:-1])
                tree_structure.setdefault(directory, []).append(path.split("/")[-1])

        return tree_structure
    def populate_treeview(self, tree, structure):
        for directory, files in structure.items():
            parent = tree.insert("", "end", text=directory, open=False)
            for file in files:
                tree.insert(parent, "end", text=file)
    def stop(self):
        if self.tree_window:  # Check if the window exists before trying to destroy it
            self.tree_window.destroy()
            self.tree_window = None  # Set it back to None after destroying
    def run(self):
        # Create a Treeview widget with a single column for filenames
        self.open_tree_window()
        self.root.mainloop()

