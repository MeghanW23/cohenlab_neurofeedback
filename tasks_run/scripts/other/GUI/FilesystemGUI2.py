import subprocess
import sys
import paramiko
import traceback
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class FileSystemGUI:
    def __init__(self, root, hostname, username, path_to_key, remote_start_path):
        # get main window
        self.root = root

        # get information for remote client connection
        self.hostname = hostname
        self.username = username
        self.path_to_key = path_to_key
        self.remote_start_path = remote_start_path


        # initialize class-wide variables
        self.tree_window = None
        self.label = None
        self.tree = None
        self.close_button = None
        self.select_button = None
        self.computer = None
        self.selected_items: dict = {}
    def run(self):
        self.computer = "e3"
        self.open_window()
    def open_window(self):
        # create tree window
        if self.computer == "e3":
            self.tree_window: tk.Toplevel = tk.Toplevel(self.root)
            self.tree_window.title("E3 File Transfer")
            self.tree_window.geometry("800x500")

        self.label: ttk.Label = ttk.Label(self.tree_window,
                                          text=f"Please Wait, Connecting to {self.computer}...",
                                          font=("Helvetica", 20))
        self.label.pack()

        # create treeview widget
        self.tree: ttk.Treeview = ttk.Treeview(self.tree_window, show="tree")
        self.tree.pack(fill=tk.BOTH, expand=True) # fill whole window, expand to fit all content given

        # create exit filesystem gui button
        self.close_button = ttk.Button(self.tree_window, text="Close", command=self.stop)
        self.close_button.pack(pady=5)

        # allow time to create widgets, then start remote client connection process
        if self.computer == "e3":
            self.root.after(100, self.connect_to_remote)
        else:
            self.root.after(100, self.get_local_filesystem)
    def connect_to_remote(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # configures the SSH client to automatically add new hosts to the local .ssh/known_hosts file

        try:
            # connect to remote client
            ssh.connect(hostname=self.hostname,
                        username=self.username,
                        key_filename=self.path_to_key)

            # run a remote script that takes in information on the remote filesystem
            stdin, stdout, stderr = ssh.exec_command(
                f"python {self.remote_start_path}/test_file.py")

            # pre-process the filesystem info from script
            file_list = stdout.read().decode().strip().splitlines()
            error_message = stderr.read().decode()

            # show error message via pop-up widget if necessary
            if error_message:
                messagebox.showerror("Error:", error_message) # Print errors if any
                sys.exit(1)
            if not file_list:
                messagebox.showerror("Error","No files found.")  # Handle case with no files
                sys.exit(1)

            ssh.close()

            self.create_tree(file_list=file_list)

        except Exception as e:
            print(f"Connection failed: {str(e)}")
            traceback.print_exc()
            self.label.config(text="Connection failed!")
    def get_local_filesystem(self):
        try:
            # Run the subprocess and capture stdout, stdin, and stderr
            result = subprocess.run(
                ["python", "/workdir/tasks_run/scripts/other/GUI/test_file_local.py"],
                capture_output=True,  # Captures stdout and stderr
                text=True  # Returns output as a string instead of bytes
            )

            # Access stdout, stderr, and return code
            stdout = result.stdout
            stderr = result.stderr

            file_list = stdout.strip().splitlines()
            error_message = stderr

            # show error message via pop-up widget if necessary
            if error_message:
                messagebox.showerror("Error:", error_message)  # Print errors if any
                sys.exit(1)
            if not file_list:
                messagebox.showerror("Error", "No files found.")  # Handle case with no files
                sys.exit(1)


            self.create_tree(file_list=file_list)


        except Exception as e:
            print(f"Get local filesystem failed: {str(e)}")
            traceback.print_exc()
            self.label.config(text="Get local filesystem failed!")
    def create_tree(self, file_list):
        self_treestruct = self.parse_data(data=file_list)
        self.populate_treeview(tree=self.tree, structure=self_treestruct)

        self.label.config(text="Choose desired file or directory")

        # create the button to select the desired file / dir
        self.select_button: ttk.Button = ttk.Button(self.tree_window,
                                                    text="Select",
                                                    command=self.on_item_selected)
        self.select_button.pack(pady=5)
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
    def on_item_selected(self):
        if self.tree.selection():  # Check if any item is selected
            selected_item = self.tree.selection()[0]  # Get the selected item
            item_name = self.tree.item(selected_item, "text")  # Get the filename
            full_path = selected_item  # The iid is set to the full path during insertion

            self.label.config(text=f"Selected: {item_name}")

            self.selected_items[self.computer] = item_name

        if self.computer == "e3":
            self.computer = "local"
            self.close_window()
            self.open_window()

        else:
            self.close_window()
            self.transfer()
    def stop(self):
        if self.tree_window:  # Check if the window exists before trying to destroy it
            self.tree_window.destroy()
            self.tree_window = None  # Set it back to None after destroying
    def close_window(self):
        # initialize class-wide variables
        self.tree.destroy()
        self.label.destroy()
        self.select_button.destroy()
        self.close_button.destroy()

        # initialize class-wide variables
        self.label = None
        self.tree = None
        self.close_button = None
        self.select_button = None

    def transfer(self):
        pass
