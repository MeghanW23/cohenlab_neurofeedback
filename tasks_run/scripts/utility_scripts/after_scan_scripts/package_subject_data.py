import os
import shutil
import subprocess
import sys 
from datetime import datetime
from itertools import chain
import glob
from tkinter import messagebox, scrolledtext
from typing import Optional
import tkinter as tk
from tkinter import filedialog
# add ../../scripts/ dir to system paths to import scripts from ../../scripts/
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import ScriptManager
import FileHandler
import settings

def open_editable_file_popup(textfile_path: str):
    # add a experimenter notes section
    with open(file=textfile_path, mode="a") as log:
        log.write(f"\n\n=========================== EXPERIMENTER NOTES HERE ===========================\n")
        log.write(f"\n\n\n\n\n\n\n===============================================================================")
        

    # create the main window
    root = tk.Tk()
    root.title("Text File Editor")
    root.geometry("800x400")

    def save_file():
        # save the contents of the text area back to the file.
        if textfile_path:
            with open(textfile_path, 'w') as file:
                file.write(text_area.get("1.0", tk.END))
            root.destroy()
            return 
        
        else:
            messagebox.showwarning("Error", "No file selected to save.")
            root.destroy()
            return 

    if textfile_path:
        tk.Label(master=root, text=f"Fill in any information you can for any missing info").pack(padx=5, pady=2)
        tk.Label(master=root, text=f"Utilize the experimenter notes section to write any additonal info on the session").pack(padx=5, pady=2)

        # add a scrolled text widget to edit file content
        text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=20)
        text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # read the file and insert its content into the text widget
        with open(textfile_path, 'r') as file:
            content = file.read()
            text_area.insert(tk.END, content)
        
        # scroll to the bottom of the text area
        text_area.yview_moveto(1.0)

        # add a save button
        save_button = tk.Button(root, text="Save and Exit", command=save_file)
        save_button.pack(pady=5)

    else:
        messagebox.showwarning("No File Selected", "No file was selected to open.")
        root.destroy()

    root.mainloop()

def get_session_number() -> int: 
    while True:
        try:
            session_num: int = int(input("Please enter the session number: ").lower().strip())
            if not (0 < session_num <= 9):
                raise ValueError
            else: 
                return session_num
            
        except ValueError: 
            print(f"The session number must be a digit between 1 or 9")

def get_scan_date() -> str:
    while True:
        try:
            date_str: str = input("Enter a the date of the scan (YYYY-MM-DD): ").lower().strip()
            selected_date: datetime.date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if selected_date >= datetime.now().date():
                print("The date must be in the past. Please try again.")
            else:
                return selected_date.strftime("%Y%m%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

def find_paths(parent_dir: str, pid: str, timestamp:str) -> list[str]:
    matching_paths: list[str] = []

    # walk through every directory and file in the parent directory
    for root, dirs, files in os.walk(parent_dir):
        # check if the root directory contains the substrings

        # ignore the subject data dir 
        if settings.SUBJECT_DATA_DIR in root:
            continue

        if pid in root and timestamp in root:
            matching_paths.append(root)
        
        # check files in the current directory for the substrings
        for file in files:
            full_path: str = os.path.join(root, file)
            if pid in full_path and timestamp in full_path:
                matching_paths.append(full_path)

    return matching_paths

def find_paths_with_keywords(expected_paths: dict, pid:str, timestamp:str) -> tuple[list[str], list[str]]:

    all_files_to_include: list[list[str]] = []
    missing_files: list[str] = []

    for directory, keyword in ((dir, kw) for dir, kws in expected_paths.items() for kw in kws):
            
            # matching files include a participant id, keyword, and timestamp 
            matching_files: list[str] = list(
                set(glob.glob(os.path.join(directory, f"*{pid}*")))
                .intersection(set(glob.glob(os.path.join(directory, f"*{keyword}*"))))
                .intersection(set(glob.glob(os.path.join(directory, f"*{timestamp}*"))))
                )

            if matching_files == []: 
                print(f"WARNING: Could not find any matching files with keyword: '{keyword}' in directory: {directory}\n")
                missing_files.append(f"{directory}/*{keyword}*")
            else:
                all_files_to_include.append(matching_files)

    # convert list[list[str]] to list[str]
    log_list: list[str] = list(chain.from_iterable(all_files_to_include)) 
    
    # some keywords from expected_paths must show up in more than one file
    msit_score_file_count: int = 0
    rifg_score_file_count: int = 0
    for file in log_list:
        if "msit_scores" in file: msit_score_file_count += 1
        if "rifg_scores" in file: rifg_score_file_count += 1
    
    if msit_score_file_count < 2:
        print(f"WARNING: {msit_score_file_count} msit score csv(s) found, but there should be 2.\n")
    if rifg_score_file_count < 2: 
        print(f"WARNING: Only {rifg_score_file_count} rifg score csv(s) found, but there should be 2.\n")
    
    return log_list, missing_files

def print_and_log_files(log_list: list[str], log_path: str, missing_files: list[str], output_dir: str): 
    files_found: dict = {}
    for file in sorted(log_list):
        if not os.path.dirname(file) in files_found:
            files_found[os.path.dirname(file)] = [file]
        else: 
            files_found[os.path.dirname(file)].append(file)

    with open(file=log_path, mode="a") as log:

        if missing_files:
            log.write("\nCould not find the following expected log files - ENTER MANUALLY (if they exist):\n")
            for file in missing_files:
                relative_path: str = (os.path.relpath(file, output_dir)).replace("../", "")
                log.write(f"   {relative_path}\n")

        log.write("\nLogs included in this directory: \n")
        for key, values in files_found.items():
            log.write(f"\nIn {os.path.relpath(key, output_dir)}:\n")
            for value in values:
                    log.write(f"   {os.path.basename(value)}\n")
        
def select_dicom_dir(timestamp:str) -> Optional[str]:
    # select an associated dicom dir to add to the output directory
    while True: 

        choose_if_add_dcms: str = input(f"\nDo you want to include a real-time DICOM directory from the sambashare directory? (y/n): ").lower().strip()
        
        if not choose_if_add_dcms in ["y", "n"]:

            print(f"Please enter either 'y' or 'n'")

        elif choose_if_add_dcms == 'y':

            while True:
                
                samba_dirs: list[str] = [dir for dir in os.listdir(settings.SAMBASHARE_DIR_PATH) if os.path.isdir(os.path.join(settings.SAMBASHARE_DIR_PATH, dir)) and timestamp in dir]
                
                print(f"Available directories with the given scan date: ")
                for index, element in enumerate(samba_dirs, start=1):
                    print(f"({index}) {element}")
                
                try:
                    dcm_chosen: int = int(input(f"Please enter the associated number with the DICOM directory you want to include: ").lower().strip())
                    
                    if not 0 < dcm_chosen <= len(samba_dirs): 
                        raise ValueError
                    else: 
                        return os.path.join(settings.SAMBASHARE_DIR_PATH, samba_dirs[dcm_chosen - 1])

                except ValueError: 
                    print(f"Please enter a number between 1 and {len(samba_dirs)}")

                
        elif choose_if_add_dcms == 'n':
            return 

def make_output_log(output_directory: str, pid: str, session_num: str, timestamp: str, logs_used: list[str]) -> str:
    output_log: str = os.path.join(output_directory, f"session_info.log")

    with open(file=output_log, mode="w") as log:
        log.write(f"Log created at {datetime.now().strftime('%m/%d/%Y %H:%M:%S')} by {os.getlogin()}\n\n")
        log.write(f"Participant ID: {pid}\n")
        log.write(f"Scan Date: {timestamp[4:6]}/{timestamp[6:8]}/{timestamp[0:4]}\n")
        log.write(f"Session Number: {session_num}\n\n")

        roi_used, registration_method, registered_mask_path = find_registration_info(log_list=logs_used)
        reg_relative_path: str = (os.path.relpath(registered_mask_path, output_directory)).replace("../", "")
        log.write(f"Registered Mask Used: {reg_relative_path}\n")
        log.write(f"ROI Used: {roi_used}\n")
        log.write(f"Registration Method: {registration_method}\n\n")

        
        threshold, localized_mask_path = find_localization_info(log_list=logs_used)
        loc_relative_path: str = (os.path.relpath(localized_mask_path, output_directory)).replace("../", "")
        log.write(f"Localized Mask Used: {loc_relative_path}\n")
        log.write(f"Mask Threshold (z-score): {threshold}\n")

    return output_log

def make_output_directory(pid: str, session_num: str, timestamp:str) -> str:
    output_directory_path: str = os.path.join(settings.SUBJECT_DATA_DIR, f"{pid}_s{session_num}_{timestamp}_realtime_collected_data")
    try:
        os.makedirs(name=output_directory_path, exist_ok=False)
    except FileExistsError:
        print(f"The output directory: {output_directory_path} already exists.")
        while True:
            overwrite_answer: str = input("Overwrite the directory? (y/n): ").lower().strip()
            if not overwrite_answer in ["y", "n"]:
                print(f"Please enter 'y' or 'n'")
            elif overwrite_answer == "n":
                print(f"Ok, exiting now.")
                sys.exit()
            elif overwrite_answer == 'y':
                shutil.rmtree(output_directory_path)
                os.makedirs(name=output_directory_path, exist_ok=False)
                break

    return output_directory_path

def find_registration_info(log_list: list[str]) -> tuple[str, str, str]:
    # from the filename of the registrated mask, get the roi and the registration method used
    registered_mask_paths: list[str] = []
    for file in log_list: 
        if "registered" in os.path.basename(file):
            registered_mask_paths.append(file)
    
    if len(registered_mask_paths) < 1: 
        print(f"WARNING: Could not determine registration method and ROI used during the session (no registration mask found)")
        return "Could Not Determine, ENTER MANUALLY", "Could Not Determine, ENTER MANUALLY", "Could Not Determine, ENTER MANUALLY"

    elif len(registered_mask_paths) > 1: 
        print(f"\nMore than one registered mask was found for this participant and date:")
        while True: 
            for index, mask in enumerate(registered_mask_paths, start=1):
                print(f"({index}) {mask}")

            try: 
                choice: int = int(input("Please select the mask used during the session: ").lower().strip())
                if not 1 <= choice <= len(registered_mask_paths): 
                    raise ValueError
                else:
                    registered_mask_path: str = registered_mask_paths[choice - 1]
                    print(registered_mask_path)
                    break 
            except ValueError: 
                print(f"Please choose a number between 1 and {len(registered_mask_paths)}")
    else:
        registered_mask_path: str = registered_mask_paths[0]
    
    roi: str = "Could Not Determine, ENTER MANUALLY"
    if "_acc_" in registered_mask_path:
        roi = "Anterior Cingulate Cortex"
    elif "_rifg_" in registered_mask_paths:
        roi = "Right Inferior Frontal Gyrus"
    elif "_motor_" in registered_mask_paths:
        roi = "Motor Cortex"
    else: 
        print(f"WARNING: Could not determine ROI used as the neurofeedback mask during the session")
    
    registration_method: str = "Could Not Determine, ENTER MANUALLY"
    if "_e3_" in registered_mask_path:
        registration_method = "EasyReg Via E3 Pipeline"
    elif "_fnirt_" in registered_mask_paths:
        registration_method = "FNIRT/FLIRT Via Host Machine Pipeline"
    else: 
        print(f"WARNING: Could not determine registration method used during the session")
    return roi, registration_method, registered_mask_path

def find_localization_info(log_list: list[str]) -> tuple[str, str]:
    # from the filename of the registrated mask, get the roi and the registration method used
    localized_mask_paths: list[str] = []
    for file in log_list: 
        if "localized" in os.path.basename(file):
            localized_mask_paths.append(file)
    
    if len(localized_mask_paths) < 1: 
        print(f"WARNING: Could not determine localization information (no localized mask found)")
        return "Could Not Determine, ENTER MANUALLY", "Could Not Determine, ENTER MANUALLY"

    elif len(localized_mask_paths) > 1: 
        print(f"\nMore than one localized mask was found for this participant and date:")
        while True: 
            for index, mask in enumerate(localized_mask_paths, start=1):
                print(f"({index}) {os.path.basename(mask)}")

            try: 
                choice: int = int(input("Please select the mask used during the session: ").lower().strip())
                if not 1 <= choice <= len(localized_mask_paths): 
                    raise ValueError
                else:
                    localized_mask_path: str = localized_mask_paths[choice - 1]
                    break 
            except ValueError: 
                print(f"Please choose a number between 1 and {len(localized_mask_paths)}")
    else:
        localized_mask_path: str = localized_mask_paths[0]
    
    filename_split: list[str] = (os.path.basename(localized_mask_path).strip()).split("_")
    threshold: str = f"{filename_split[5]}.{filename_split[6]}"

    return threshold, localized_mask_path

def copy_logs(log_list: list[str], output_dir: str, expected_paths: dict) -> list[str]:  
    post_copy_paths: list[str] = []

    # create log 
    log_output_dir: str = os.path.join(output_dir, "logs")
    os.makedirs(log_output_dir)
    
    for dir in expected_paths:
        os.makedirs(name=os.path.join(log_output_dir, dir.split("/data/")[1]))
    
    for log in log_list:
        if "/data/" in log: 
            dest_path: str = os.path.join(log_output_dir, log.split("/data/")[1])
            shutil.copy(src=log, dst=dest_path)
            post_copy_paths.append(dest_path)
        else: 
            dest_path: str = os.path.join(log_output_dir, os.path.basename(log))
            shutil.copy(src=log, dst=dest_path)
            post_copy_paths.append(dest_path)
    
    return post_copy_paths

def copy_dicom_dir(dicom_dir_path: str, output_dir: str) -> str:
    print(f"Copying all DICOMs to {os.path.join(output_dir, f'sambashare_dicoms')}...")
    shutil.copytree(src=dicom_dir_path, dst=os.path.join(output_dir, f"sambashare_dicoms"))
    print("All DICOMs copied.")

    return os.path.join(output_dir, f'sambashare_dicoms')

def log_dicoms(output_dicom_dir_path: str, output_log:str):
    with open(file=output_log, mode="a") as log:
        log.write(f"\n\nDICOMs included from the sambashare directory: \n")
        for dicom in sorted(os.listdir(output_dicom_dir_path)):
            log.write(f"{dicom}\n")

def copy_file_to_remote(local_dir):

    try:
        # Construct the rsync command
        command = [
            "rsync",
            "-avz",  # a: archive mode, v: verbose, z: compress files during transfer
            local_dir,
            f"{input('Enter your chid: ').lower().strip()}@e3-login.tch.harvard.edu:{settings.E3_PATH_TO_SUBJECT_DATA}"
        ]
        # Execute the command
        subprocess.run(command, check=True)

        print(f"Data sent to: {settings.E3_PATH_TO_SUBJECT_DATA}")

    except subprocess.CalledProcessError as e:
        print(f"Error copying file: {e}")


# we expect that, post-session, each of these directories should have files that include each keyword in each record's list
expected_paths: dict = {

    # RIFG Task
    settings.RIFG_EVENT_CSV_DIR: ["postRIFG_events", "preRIFG_events"],
    settings.RIFG_LOG_DIR: ["pre_rifg_log", "post_rifg_log", "rifg_task_pre", "rifg_task_post"], # rifg_task == .csv and pre_rifg/post_rifg == .txt
    settings.RIFG_SCORE_LOG_DIR: ["rifg_scores"],
    
    # MSIT Task 
    settings.MSIT_LOG_DIR: ["MSIT_PRE", "MSIT_POST"],
    settings.MSIT_SCORE_LOG_DIR: ["msit_scores"], 
    
    # NFB Task
    settings.NFB_LOG_DIR: ["calculator_script", "data_dictionary"],
    settings.NFB_SCORE_LOG_DIR: ["nfb_scores"],

    # Rest Task
    settings.REST_LOG_DIR: ["rest_log"],

    # Localizer and Mask Material
    settings.LOCALIZER_LOG_DIR: ["localizer_log"],
    settings.ROI_MASK_DIR_PATH: ["registered", "localized"],
    settings.LOCALIZER_SECONDARY_MATERIAL_DIR_PATH: ["design_matrix", "z_map", "contrast_matrix"]   
}

# get the participant id and make sure its an already existing particpant id (confirm_exists=True) 
pid: str = FileHandler.validate_inputted_pid_is_new(
    inputted_pid=ScriptManager.get_participant_id(),
    confirm_exists=True
    )

# get the date of the scan 
timestamp: str = get_scan_date()

# get the session number of the scan 
session_num: str = get_session_number()

# check for files that have the correct pid, keyword, and timestamp
print(f"\nSearching for files that include:")
print(f"  Timestamp: {timestamp}")
print(f"  Participant ID: {pid}\n")
found_expected_paths, missing_files = find_paths_with_keywords(expected_paths=expected_paths, pid=pid, timestamp=timestamp)
if not found_expected_paths:
    print(f"Could not find any logs. Please check that your inputted participant ID and scan date are accurate, then try again.")
    sys.exit(1) # no data found 


# check for additional paths: these unexpected paths have the correct pid and timestamp but not a keyword listed in expected_paths
found_unexpected_paths: list[str] = list(set(find_paths(parent_dir=settings.PROJECT_DIRECTORY, pid=pid,timestamp=timestamp)) - set(found_expected_paths))
if found_unexpected_paths: 
    print(f"\nFound Additional Paths:")
    for path in found_unexpected_paths:
        print(path)
    print(" ")

    # put all files in a list, expected and unexpected
    all_logs: list[str] = found_expected_paths + found_unexpected_paths
else: 
    all_logs: list[str] = found_expected_paths

print(f"Total Logs Included: {len(all_logs)}")

if all_logs: # only make output dir for data, etc. if theres logs, else theres not really a point
    outDir: str = make_output_directory(pid=pid, session_num=session_num, timestamp=timestamp)

    # make a log to store information about the session 
    output_log: str = make_output_log(output_directory=outDir, pid=pid, session_num=session_num, timestamp=timestamp, logs_used=all_logs)

    # copy all logs 
    copied_log_paths: str = copy_logs(log_list=all_logs, output_dir=outDir, expected_paths=expected_paths)

    # print file list to log
    print_and_log_files(log_list=copied_log_paths, log_path=output_log, missing_files=missing_files, output_dir=os.path.basename(outDir))
    

    # add a real-time dicom dir if included 
    dicom_dir_path: str = select_dicom_dir(timestamp=timestamp)
    if dicom_dir_path:
        output_dicom_path: str = copy_dicom_dir(dicom_dir_path=dicom_dir_path, output_dir=outDir)
        log_dicoms(output_dicom_dir_path=output_dicom_path, output_log=output_log)

  
    print(f"All logs and data have been sent to the output directory at: {outDir}")

    open_editable_file_popup(textfile_path=output_log)

# TODO send to e3
while True: 
    copy_to_e3: str = input(f"Send Directory to E3? (y/n): ").lower().strip()
    if not copy_to_e3 in ["y", "n"]:
        print(f"Please enter either 'y' or 'n'")
    elif copy_to_e3 == 'n':
        print(f"All Set!")
        sys.exit(0)
    elif copy_to_e3 == 'y':
        print(f"Copying {outDir} to E3 now...")
        copy_file_to_remote(local_dir=outDir)
