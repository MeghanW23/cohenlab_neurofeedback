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
        self.file_list = None
        self.select_button = None
    def open_window(self):
        # create tree window
        self.tree_window = tk.Toplevel(self.root)
        self.tree_window.title("E3 File Transfer")
        self.tree_window.geometry("800x500")

        # create label widget, write starting text
        self.label = ttk.Label(self.tree_window,
                               text="Please Wait, Connecting to Remote Client ...",
                               font=("Helvetica", 20))
        self.label.pack()

        # create treeview widget
        self.tree = ttk.Treeview(self.tree_window, show="tree")
        self.tree.pack(fill=tk.BOTH, expand=True) # fill whole window, expand to fit all content given

        # create exit filesystem gui button
        self.close_button = ttk.Button(self.tree_window, text="Close", command=self.stop)
        self.close_button.pack(pady=5)

        # allow time to create widgets, then start remote client connection process
        self.root.after(100, self.connect_to_remote)

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
            self.file_list = stdout.read().decode().strip().splitlines()
            error_message = stderr.read().decode()

            # show error message via pop-up widget if necessary
            if error_message:
                messagebox.showerror("Error:", error_message) # Print errors if any
                sys.exit(1)
            if not self.file_list:
                messagebox.showerror("Error","No files found.")  # Handle case with no files
                sys.exit(1)

            self_treestruct = self.parse_data(data=self.file_list)
            self.populate_treeview(tree=self.tree, structure=self_treestruct)

            self.label.config(text="Choose desired file or directory")

            ssh.close()

            # create the button to select the desired file / dir
            self.select_button = ttk.Button(self.tree_window,
                                            text="Select",
                                            command=lambda: self.on_item_selected(get_next=True))
            self.select_button.pack(pady=5)

        except Exception as e:
            print(f"Connection failed: {str(e)}")
            traceback.print_exc()
            self.label.config(text="Connection failed!")

    # make dictionary recording the structure of the tree
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

    # add the files to the widget from the parse_data() dictionary
    def populate_treeview(self, tree, structure):
        for directory, files in structure.items():
            parent = tree.insert("", "end", text=directory, open=False)
            for file in files:
                tree.insert(parent, "end", text=file)

    def on_item_selected(self, get_next: bool = True):
        if self.tree.selection():  # Check if any item is selected
            selected_item = self.tree.selection()[0]  # Get the selected item
            item_name = self.tree.item(selected_item, "text")  # Get the filename
            full_path = selected_item  # The iid is set to the full path during insertion

            self.label.config(text=f"Selected: {item_name}")

            if get_next:
                self.select_button = None
                self.get_local_filesystem()


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
            return_code = result.returncode

            self.file_list = stdout.strip().splitlines()
            error_message = stderr

            # show error message via pop-up widget if necessary
            if error_message:
                messagebox.showerror("Error:", error_message)  # Print errors if any
                sys.exit(1)
            if not self.file_list:
                messagebox.showerror("Error", "No files found.")  # Handle case with no files
                sys.exit(1)

            self_treestruct = self.parse_data(data=self.file_list)
            self.populate_treeview(tree=self.tree, structure=self_treestruct)

            # create the button to select the desired file / dir
            self.select_button = ttk.Button(self.tree_window, text="Select", command=self.on_item_selected)
            self.select_button.pack(pady=5)


        except Exception as e:
            print(f"Get local filesystem failed: {str(e)}")
            traceback.print_exc()
            self.label.config(text="Get local filesystem failed!")

    def run(self):
        self.open_window()

    def stop(self):
        if self.tree_window:  # Check if the window exists before trying to destroy it
            self.tree_window.destroy()
            self.tree_window = None  # Set it back to None after destroying