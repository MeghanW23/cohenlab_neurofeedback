import os.path

import paramiko
import tkinter as tk
from tkinter import ttk
import sys
from tkinter import messagebox

class GetFileSystemGUI:
    def __init__(self, root, hostname, username, path_to_key, remote_start_path):
        self.root = root
        self.hostname = hostname
        self.username = username
        self.path_to_key = path_to_key
        self.remote_start_path = remote_start_path

        # Create a Treeview widget with a single column for filenames
        self.tree = ttk.Treeview(self.root, show="tree")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_item_selected)

        self.connect_to_remote()

    def on_item_selected(self, event):
        if self.tree.selection():  # Check if any item is selected
            selected_item = self.tree.selection()[0]  # Get the selected item
            item_name = self.tree.item(selected_item, "text")  # Get the filename
            print(f"Selected: {item_name}")  # Print the selected filename

    def connect_to_remote(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(hostname=self.hostname, username=self.username, key_filename=self.path_to_key)
            stdin, stdout, stderr = ssh.exec_command(f"python {self.remote_start_path}/print_tree.py")  # Retrieve detailed file list
            file_list = stdout.read().decode().strip().splitlines()

            error_message = stderr.read().decode()
            if error_message:
                messagebox.showerror("Error:", error_message) # Print errors if any
                sys.exit(1)

            if not file_list:
                messagebox.showerror("Error","No files found.")  # Handle case with no files
                sys.exit(1)

            # Store the already inserted directories to avoid duplicates
            inserted_directories = {}

            for item in file_list:
                path = item.split(": ")[1]  # Extract the path from the string
                item_name = os.path.basename(path)  # Get the base name of the item
                parent_directory = os.path.dirname(path)  # Get the parent directory

                if "file:" in item:
                    # Insert file under its parent directory in the tree
                    # Ensure parent directory is inserted first
                    if parent_directory not in inserted_directories:
                        # Insert the parent directory if it's not already in the tree
                        self.tree.insert("", "end", text=os.path.basename(parent_directory), iid=parent_directory)
                        inserted_directories[parent_directory] = True  # Mark this directory as inserted

                    # Now insert the file under the parent directory
                    self.tree.insert(parent_directory, "end", text=item_name)  # Use the parent directory as parent

                else:  # Directory case
                    if item == self.remote_start_path:
                        # Insert as root directory if it matches remote start path
                        self.tree.insert("", "end", text=item_name, iid=item)  # Use empty string for root
                        inserted_directories[item] = True  # Mark this directory as inserted
                    else:
                        # Insert the directory item, ensuring parent is added first
                        if parent_directory not in inserted_directories:
                            # Insert the parent directory if it's not already in the tree
                            self.tree.insert("", "end", text=os.path.basename(parent_directory), iid=parent_directory)
                            inserted_directories[parent_directory] = True  # Mark this directory as inserted

                        # Insert the current directory under its parent
                        self.tree.insert(parent_directory, "end", text=item_name,
                                         iid=item)  # Use the parent directory as parent

            ssh.close()

        except Exception as e:
            print(f"Connection failed: {str(e)}")

    def run(self):
        self.root.mainloop()


# Create an instance of the GUI and run it
if __name__ == "__main__":
    root = tk.Tk()
    app = GetFileSystemGUI(root=root,
                            hostname="e3-login.tch.harvard.edu",
                            username="ch246081",
                            path_to_key="/workdir/.ssh/docker_e3_key_ch246081",
                            remote_start_path="/lab-share/Neuro-Cohen-e2/Public/projects/ADHD_NFB")

    app.run()
