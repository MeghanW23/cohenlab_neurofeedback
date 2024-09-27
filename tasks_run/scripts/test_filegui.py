import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import subprocess
import os

def grab_file():
    # Open a file dialog to select a file
    file_path = filedialog.askopenfilename()
    if file_path:
        remote_path = remote_entry.get()
        if remote_path:
            transfer_file(file_path, remote_path)
        else:
            messagebox.showwarning("No Destination", "Please specify a remote destination.")
    else:
        messagebox.showwarning("No Selection", "No file was selected.")

def transfer_file(file_path, remote_path):
    try:
        # Construct the rsync command
        command = ['rsync', '-avz', file_path, remote_path]
        subprocess.run(command, check=True)
        messagebox.showinfo("Transfer Complete", f"File transferred to: {remote_path}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Transfer Error", f"Error during transfer: {e}")

# Create the main application window
root = tk.Tk()
root.title("File Selector with rsync")
root.geometry("400x200")

# Create a button to grab a file
select_button = tk.Button(root, text="Select File", command=grab_file)
select_button.pack(pady=10)

# Entry for remote destination
remote_label = tk.Label(root, text="Remote Destination (e.g. user@remote_host:/path/):")
remote_label.pack(pady=5)
remote_entry = tk.Entry(root, width=40)
remote_entry.pack(pady=5)

# Start the GUI event loop
root.mainloop()
