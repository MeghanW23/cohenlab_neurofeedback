import paramiko
import tkinter as tk
from tkinter import ttk

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
            stdin, stdout, stderr = ssh.exec_command(f"ls -l {self.remote_start_path}")  # Retrieve detailed file list
            file_list = stdout.read().decode().strip().splitlines()

            error_message = stderr.read().decode()
            if error_message:
                print("Error:\n", error_message)  # Print errors if any
                return

            if not file_list:
                print("No files found.")  # Handle case with no files
                return

            # Populate the Treeview with only filenames
            for item in file_list:
                parts = item.split()  # Split the line into parts
                if len(parts) >= 9:  # At least 9 parts for 'ls -l'
                    name = " ".join(parts[8:])  # Handle spaces in filenames
                    self.tree.insert("", "end", text=name)  # Insert only the filename

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
